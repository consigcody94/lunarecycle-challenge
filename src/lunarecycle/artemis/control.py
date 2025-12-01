"""
ARTEMIS-R Control System

Real-time control and automation for the ARTEMIS-R recycling system.
Implements safety interlocks, process sequencing, and optimization.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Optional, Callable
import threading
import time


class OperatingMode(Enum):
    """System operating modes."""

    AUTONOMOUS = auto()  # Full AI control
    SUPERVISED = auto()  # AI with human oversight
    MANUAL = auto()  # Direct human control
    SAFE = auto()  # Safety shutdown mode
    MAINTENANCE = auto()  # Maintenance mode


class AlarmSeverity(Enum):
    """Alarm severity levels."""

    INFO = auto()
    WARNING = auto()
    ALARM = auto()
    CRITICAL = auto()


@dataclass
class Alarm:
    """System alarm."""

    timestamp: datetime
    severity: AlarmSeverity
    source: str
    message: str
    acknowledged: bool = False


@dataclass
class Setpoint:
    """Process setpoint with limits."""

    name: str
    value: float
    unit: str
    low_limit: float
    high_limit: float
    low_alarm: Optional[float] = None
    high_alarm: Optional[float] = None


class SafetyInterlock:
    """Safety interlock condition."""

    def __init__(
        self,
        name: str,
        check_function: Callable[[], bool],
        trip_action: Callable[[], None],
        reset_action: Optional[Callable[[], None]] = None,
    ):
        self.name = name
        self.check = check_function
        self.trip = trip_action
        self.reset = reset_action
        self.tripped = False
        self.trip_time: Optional[datetime] = None

    def evaluate(self) -> bool:
        """Evaluate interlock and trip if needed."""
        if not self.check():
            if not self.tripped:
                self.tripped = True
                self.trip_time = datetime.now()
                self.trip()
            return False
        return True


class PIDController:
    """PID controller for temperature/pressure control."""

    def __init__(
        self,
        kp: float = 1.0,
        ki: float = 0.1,
        kd: float = 0.05,
        output_min: float = 0.0,
        output_max: float = 100.0,
    ):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_min = output_min
        self.output_max = output_max

        self.setpoint = 0.0
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time: Optional[datetime] = None

    def update(self, process_value: float, current_time: datetime) -> float:
        """Calculate PID output."""
        error = self.setpoint - process_value

        if self.last_time is None:
            dt = 1.0
        else:
            dt = (current_time - self.last_time).total_seconds()

        # Proportional
        p_term = self.kp * error

        # Integral with anti-windup
        self.integral += error * dt
        self.integral = max(
            self.output_min / self.ki if self.ki != 0 else -1e6,
            min(self.output_max / self.ki if self.ki != 0 else 1e6, self.integral),
        )
        i_term = self.ki * self.integral

        # Derivative
        d_term = self.kd * (error - self.last_error) / dt if dt > 0 else 0

        # Calculate output
        output = p_term + i_term + d_term
        output = max(self.output_min, min(self.output_max, output))

        self.last_error = error
        self.last_time = current_time

        return output


@dataclass
class ProcessSequence:
    """Automated process sequence."""

    name: str
    steps: list[dict]
    current_step: int = 0
    running: bool = False
    paused: bool = False
    start_time: Optional[datetime] = None


class ARTEMISController:
    """
    Main control system for ARTEMIS-R.

    Manages:
    - Operating mode selection
    - Safety interlocks
    - Process sequencing
    - PID control loops
    - Alarm management
    """

    def __init__(self):
        self.mode = OperatingMode.MANUAL
        self.alarms: list[Alarm] = []
        self.active_alarms: list[Alarm] = []
        self.interlocks: list[SafetyInterlock] = []

        # PID controllers for thermal zones
        self.thermal_pids = {
            "reactor": PIDController(kp=2.0, ki=0.1, kd=0.5, output_max=100.0),
            "extruder_zone1": PIDController(kp=1.5, ki=0.08, kd=0.3, output_max=100.0),
            "extruder_zone2": PIDController(kp=1.5, ki=0.08, kd=0.3, output_max=100.0),
            "extruder_zone3": PIDController(kp=1.5, ki=0.08, kd=0.3, output_max=100.0),
            "extruder_zone4": PIDController(kp=1.5, ki=0.08, kd=0.3, output_max=100.0),
            "press_upper": PIDController(kp=1.0, ki=0.05, kd=0.2, output_max=100.0),
            "press_lower": PIDController(kp=1.0, ki=0.05, kd=0.2, output_max=100.0),
        }

        # Process setpoints
        self.setpoints = {
            "reactor_temp": Setpoint(
                "Reactor Temperature",
                400.0,
                "°C",
                350.0,
                450.0,
                low_alarm=340.0,
                high_alarm=460.0,
            ),
            "reactor_pressure": Setpoint(
                "Reactor Pressure", 101.3, "kPa", 50.0, 200.0, high_alarm=250.0
            ),
            "extruder_temp": Setpoint(
                "Extruder Temperature", 200.0, "°C", 150.0, 280.0, high_alarm=300.0
            ),
            "press_temp": Setpoint(
                "Press Temperature", 180.0, "°C", 100.0, 200.0, high_alarm=220.0
            ),
            "press_pressure": Setpoint(
                "Press Force", 20.0, "MPa", 5.0, 50.0, high_alarm=55.0
            ),
        }

        # Process sequences
        self.sequences: dict[str, ProcessSequence] = {}
        self._define_sequences()

        # Sensor values (simulated)
        self.sensor_values: dict[str, float] = {}

        # Control outputs
        self.outputs: dict[str, float] = {}

        # System state
        self.running = False
        self.estop_active = False
        self.current_time = datetime.now()

        # Initialize safety interlocks
        self._setup_interlocks()

    def _setup_interlocks(self) -> None:
        """Configure safety interlocks."""
        # Emergency stop
        self.interlocks.append(
            SafetyInterlock(
                name="E-Stop",
                check_function=lambda: not self.estop_active,
                trip_action=self._emergency_stop,
            )
        )

        # Over-temperature protection
        self.interlocks.append(
            SafetyInterlock(
                name="Reactor Over-Temp",
                check_function=lambda: self.sensor_values.get("reactor_temp", 0) < 500,
                trip_action=lambda: self._shutdown_module("thermal"),
            )
        )

        # HF gas detection
        self.interlocks.append(
            SafetyInterlock(
                name="HF Detection",
                check_function=lambda: self.sensor_values.get("hf_ppm", 0) < 1.0,
                trip_action=self._hf_alarm_response,
            )
        )

        # Pressure relief
        self.interlocks.append(
            SafetyInterlock(
                name="Reactor Over-Pressure",
                check_function=lambda: self.sensor_values.get("reactor_pressure", 0) < 300,
                trip_action=lambda: self._open_relief_valve("reactor"),
            )
        )

    def _define_sequences(self) -> None:
        """Define automated process sequences."""
        # Thermal processing sequence
        self.sequences["thermal_batch"] = ProcessSequence(
            name="Thermal Batch Processing",
            steps=[
                {"action": "check_material", "timeout": 60},
                {"action": "preheat", "target": 350, "timeout": 1800},
                {"action": "load_batch", "timeout": 300},
                {"action": "seal_reactor", "timeout": 60},
                {"action": "ramp_temp", "target": 400, "rate": 10, "timeout": 600},
                {"action": "hold_temp", "duration": 2700},
                {"action": "cool_down", "target": 150, "timeout": 1800},
                {"action": "vent_gases", "timeout": 300},
                {"action": "unload_char", "timeout": 300},
                {"action": "reset", "timeout": 60},
            ],
        )

        # Extrusion sequence
        self.sequences["extrusion_run"] = ProcessSequence(
            name="Extrusion Run",
            steps=[
                {"action": "heat_zones", "timeout": 1200},
                {"action": "prime_screw", "timeout": 300},
                {"action": "start_puller", "timeout": 60},
                {"action": "extrude", "duration": 3600},
                {"action": "purge", "timeout": 300},
                {"action": "cool_down", "timeout": 600},
            ],
        )

        # Composite pressing sequence
        self.sequences["press_cycle"] = ProcessSequence(
            name="Press Cycle",
            steps=[
                {"action": "preheat_platens", "target": 180, "timeout": 1200},
                {"action": "load_mold", "timeout": 300},
                {"action": "close_press", "force": 20, "timeout": 60},
                {"action": "hold_press", "duration": 900},
                {"action": "cool_press", "target": 80, "timeout": 600},
                {"action": "release_press", "timeout": 60},
                {"action": "eject_part", "timeout": 120},
            ],
        )

    def set_mode(self, mode: OperatingMode) -> bool:
        """Set operating mode."""
        if self.estop_active and mode != OperatingMode.SAFE:
            self._raise_alarm(
                AlarmSeverity.WARNING, "Controller", "Cannot change mode while E-Stop active"
            )
            return False

        self.mode = mode
        return True

    def start(self) -> bool:
        """Start the control system."""
        if self.estop_active:
            return False

        self.running = True
        return True

    def stop(self) -> None:
        """Stop the control system."""
        self.running = False

    def emergency_stop(self) -> None:
        """Activate emergency stop."""
        self.estop_active = True
        self._emergency_stop()

    def reset_estop(self) -> bool:
        """Reset emergency stop if safe."""
        # Check all interlocks are clear
        for interlock in self.interlocks:
            if interlock.tripped:
                self._raise_alarm(
                    AlarmSeverity.WARNING,
                    "Controller",
                    f"Cannot reset E-Stop: {interlock.name} still tripped",
                )
                return False

        self.estop_active = False
        self.mode = OperatingMode.MANUAL
        return True

    def update(self, dt_seconds: float = 1.0) -> None:
        """Update control loops (call periodically)."""
        self.current_time += timedelta(seconds=dt_seconds)

        if not self.running:
            return

        # Check safety interlocks
        for interlock in self.interlocks:
            interlock.evaluate()

        # Update PID controllers
        self._update_pid_loops()

        # Check setpoint alarms
        self._check_setpoint_alarms()

        # Execute sequences if in autonomous mode
        if self.mode == OperatingMode.AUTONOMOUS:
            self._execute_sequences()

    def _update_pid_loops(self) -> None:
        """Update all PID control loops."""
        for name, pid in self.thermal_pids.items():
            # Get process value from sensors
            pv = self.sensor_values.get(f"{name}_temp", 25.0)
            # Calculate output
            output = pid.update(pv, self.current_time)
            # Store output
            self.outputs[f"{name}_heater"] = output

    def _check_setpoint_alarms(self) -> None:
        """Check process values against setpoint alarms."""
        for name, sp in self.setpoints.items():
            pv = self.sensor_values.get(name, 0)

            # Check if alarm already exists for this source to avoid duplicates
            existing_alarm_sources = {a.source for a in self.active_alarms}

            if sp.high_alarm and pv > sp.high_alarm:
                if name not in existing_alarm_sources:
                    self._raise_alarm(
                        AlarmSeverity.ALARM, name, f"High alarm: {pv:.1f} > {sp.high_alarm:.1f} {sp.unit}"
                    )
            elif sp.low_alarm and pv < sp.low_alarm:
                if name not in existing_alarm_sources:
                    self._raise_alarm(
                        AlarmSeverity.ALARM, name, f"Low alarm: {pv:.1f} < {sp.low_alarm:.1f} {sp.unit}"
                    )

    def _execute_sequences(self) -> None:
        """Execute running process sequences."""
        for seq in self.sequences.values():
            if seq.running and not seq.paused:
                # Execute current step
                # (In real implementation, this would control actual hardware)
                pass

    def _emergency_stop(self) -> None:
        """Execute emergency stop procedures."""
        self.mode = OperatingMode.SAFE
        self.running = False

        # Disable all heaters
        for name in self.thermal_pids:
            self.outputs[f"{name}_heater"] = 0

        # Stop all motors
        self.outputs["shredder_motor"] = 0
        self.outputs["extruder_motor"] = 0
        self.outputs["conveyor_motor"] = 0

        # Open vents
        self.outputs["reactor_vent"] = 100

        self._raise_alarm(AlarmSeverity.CRITICAL, "Controller", "EMERGENCY STOP ACTIVATED")

    def _shutdown_module(self, module: str) -> None:
        """Shutdown a specific module."""
        if module == "thermal":
            self.outputs["reactor_heater"] = 0
            self.outputs["reactor_vent"] = 100
        elif module == "extruder":
            self.outputs["extruder_motor"] = 0
            for i in range(1, 5):
                self.outputs[f"extruder_zone{i}_heater"] = 0

        self._raise_alarm(AlarmSeverity.WARNING, module, f"Module {module} shutdown")

    def _hf_alarm_response(self) -> None:
        """Response to HF gas detection."""
        # Immediately stop thermal processor
        self._shutdown_module("thermal")

        # Activate scrubber at full speed
        self.outputs["scrubber_fan"] = 100

        # Alert crew
        self._raise_alarm(
            AlarmSeverity.CRITICAL, "Gas Detection", "HF GAS DETECTED - EVACUATE AREA"
        )

    def _open_relief_valve(self, system: str) -> None:
        """Open pressure relief valve."""
        self.outputs[f"{system}_relief"] = 100
        self._raise_alarm(
            AlarmSeverity.ALARM, system, f"Pressure relief valve opened on {system}"
        )

    def _raise_alarm(self, severity: AlarmSeverity, source: str, message: str) -> None:
        """Raise a new alarm."""
        alarm = Alarm(
            timestamp=self.current_time,
            severity=severity,
            source=source,
            message=message,
        )
        self.alarms.append(alarm)
        self.active_alarms.append(alarm)

    def acknowledge_alarm(self, alarm: Alarm) -> None:
        """Acknowledge an alarm."""
        alarm.acknowledged = True
        if alarm in self.active_alarms:
            self.active_alarms.remove(alarm)

    def acknowledge_all_alarms(self) -> int:
        """Acknowledge all active alarms."""
        count = len(self.active_alarms)
        for alarm in self.active_alarms:
            alarm.acknowledged = True
        self.active_alarms.clear()
        return count

    def set_setpoint(self, name: str, value: float) -> bool:
        """Set a process setpoint."""
        if name not in self.setpoints:
            return False

        sp = self.setpoints[name]
        if value < sp.low_limit or value > sp.high_limit:
            self._raise_alarm(
                AlarmSeverity.WARNING,
                name,
                f"Setpoint {value} outside limits [{sp.low_limit}, {sp.high_limit}]",
            )
            return False

        sp.value = value

        # Update corresponding PID controller
        pid_mapping = {
            "reactor_temp": "reactor",
            "extruder_temp": "extruder_zone3",
            "press_temp": "press_upper",
        }
        if name in pid_mapping:
            self.thermal_pids[pid_mapping[name]].setpoint = value

        return True

    def start_sequence(self, name: str) -> bool:
        """Start a process sequence."""
        if name not in self.sequences:
            return False

        seq = self.sequences[name]
        seq.running = True
        seq.paused = False
        seq.current_step = 0
        seq.start_time = self.current_time
        return True

    def pause_sequence(self, name: str) -> bool:
        """Pause a running sequence."""
        if name not in self.sequences:
            return False

        self.sequences[name].paused = True
        return True

    def stop_sequence(self, name: str) -> bool:
        """Stop a running sequence."""
        if name not in self.sequences:
            return False

        seq = self.sequences[name]
        seq.running = False
        seq.paused = False
        seq.current_step = 0
        return True

    def get_status(self) -> dict:
        """Get controller status."""
        return {
            "mode": self.mode.name,
            "running": self.running,
            "estop_active": self.estop_active,
            "active_alarms": len(self.active_alarms),
            "interlocks_tripped": sum(1 for i in self.interlocks if i.tripped),
            "sequences_running": sum(1 for s in self.sequences.values() if s.running),
        }

    def get_io_status(self) -> dict:
        """Get I/O status."""
        return {
            "sensors": dict(self.sensor_values),
            "outputs": dict(self.outputs),
        }
