"""
ARTEMIS-R Digital Twin

Real-time simulation and monitoring system that mirrors the physical prototype.
Provides predictive analytics, process optimization, and visualization.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Callable
import json
import math
import random

from .system import ARTEMISSystem, SystemMetrics
from .control import ARTEMISController, OperatingMode, AlarmSeverity
from .modules import ModuleState


@dataclass
class SensorData:
    """Time-series sensor data point."""

    timestamp: datetime
    sensor_id: str
    value: float
    unit: str
    quality: float = 1.0  # 0-1, data quality indicator


@dataclass
class PredictionResult:
    """Result from predictive model."""

    metric: str
    predicted_value: float
    confidence: float
    horizon_hours: float
    timestamp: datetime


@dataclass
class OptimizationSuggestion:
    """Process optimization suggestion."""

    parameter: str
    current_value: float
    suggested_value: float
    expected_improvement: float
    reasoning: str


class PhysicsEngine:
    """
    Physics-based simulation engine for process modeling.

    Models:
    - Heat transfer
    - Mass flow
    - Chemical reactions (pyrolysis kinetics)
    - Material properties
    """

    def __init__(self):
        # Physical constants
        self.stefan_boltzmann = 5.67e-8  # W/m²·K⁴
        self.gas_constant = 8.314  # J/mol·K

        # Pyrolysis kinetics (Arrhenius parameters)
        self.activation_energy = {
            "LDPE": 250000,  # J/mol
            "HDPE": 260000,
            "PP": 240000,
            "cellulose": 180000,
            "cotton": 170000,
        }
        self.pre_exponential = {
            "LDPE": 1e16,
            "HDPE": 1e17,
            "PP": 1e15,
            "cellulose": 1e14,
            "cotton": 1e13,
        }

    def calculate_heat_transfer(
        self,
        temp_hot: float,
        temp_cold: float,
        area_m2: float,
        conductivity: float,
        thickness_m: float,
    ) -> float:
        """Calculate conductive heat transfer (W)."""
        return conductivity * area_m2 * (temp_hot - temp_cold) / thickness_m

    def calculate_radiation(
        self,
        temp_k: float,
        area_m2: float,
        emissivity: float = 0.9,
    ) -> float:
        """Calculate radiative heat loss (W)."""
        return emissivity * self.stefan_boltzmann * area_m2 * temp_k**4

    def calculate_pyrolysis_rate(
        self,
        material: str,
        temp_c: float,
        mass_kg: float,
    ) -> float:
        """Calculate pyrolysis conversion rate (kg/s)."""
        if material not in self.activation_energy:
            material = "LDPE"  # Default

        temp_k = temp_c + 273.15
        ea = self.activation_energy[material]
        a = self.pre_exponential[material]

        # Arrhenius rate constant
        k = a * math.exp(-ea / (self.gas_constant * temp_k))

        # First-order reaction rate
        rate = k * mass_kg
        return rate

    def calculate_heating_time(
        self,
        mass_kg: float,
        specific_heat: float,
        temp_start: float,
        temp_end: float,
        power_w: float,
        efficiency: float = 0.85,
    ) -> float:
        """Calculate time to heat mass to target temperature (seconds)."""
        energy_needed = mass_kg * specific_heat * (temp_end - temp_start)
        effective_power = power_w * efficiency
        return energy_needed / effective_power if effective_power > 0 else float("inf")

    def simulate_reactor_thermal(
        self,
        initial_temp: float,
        target_temp: float,
        mass_kg: float,
        power_w: float,
        dt_seconds: float,
    ) -> tuple[float, float]:
        """
        Simulate reactor thermal dynamics.

        Returns: (new_temp, energy_consumed_kwh)
        """
        # Simplified thermal model
        specific_heat = 1500  # J/kg·K average for waste
        heat_loss_coeff = 50  # W/K to environment

        # Energy input
        energy_in = power_w * dt_seconds

        # Energy loss
        temp_diff = initial_temp - 25  # Ambient
        energy_loss = heat_loss_coeff * temp_diff * dt_seconds

        # Net energy
        net_energy = energy_in - energy_loss

        # Temperature change
        if mass_kg > 0:
            delta_t = net_energy / (mass_kg * specific_heat)
        else:
            delta_t = net_energy / (10 * specific_heat)  # Empty reactor mass

        new_temp = initial_temp + delta_t

        # Clamp to target
        if power_w > 0 and new_temp > target_temp:
            new_temp = target_temp
        elif power_w == 0 and new_temp < 25:
            new_temp = 25

        energy_kwh = (power_w * dt_seconds) / 3600000

        return new_temp, energy_kwh


class AIEngine:
    """
    AI/ML engine for prediction and optimization.

    Features:
    - Waste classification
    - Process parameter optimization
    - Predictive maintenance
    - Anomaly detection
    """

    def __init__(self):
        # Model states (simplified for demo)
        self.classification_accuracy = 0.95
        self.prediction_horizon_hours = 24
        self.anomaly_threshold = 3.0  # Standard deviations

        # Historical data for learning
        self.sensor_history: dict[str, list[float]] = {}
        self.prediction_history: list[PredictionResult] = []

    def classify_waste(self, features: dict) -> dict[str, float]:
        """
        Classify waste material from sensor features.

        In real implementation, this would use a trained CNN on camera images.
        """
        # Simplified classification based on features
        classifications = {
            "thermoplastic": 0.0,
            "organic": 0.0,
            "foam": 0.0,
            "textile": 0.0,
            "metal": 0.0,
        }

        # Mock classification based on features
        if features.get("density", 0) < 100:
            classifications["foam"] = 0.8
        elif features.get("reflectivity", 0) > 0.7:
            classifications["metal"] = 0.9
        elif features.get("flexibility", 0) > 0.6:
            classifications["thermoplastic"] = 0.7
        else:
            classifications["organic"] = 0.5

        return classifications

    def predict_maintenance(
        self,
        sensor_data: dict[str, list[float]],
        current_time: datetime,
    ) -> list[PredictionResult]:
        """Predict maintenance needs based on sensor trends."""
        predictions = []

        for sensor_id, values in sensor_data.items():
            if len(values) < 10:
                continue

            # Simple trend analysis
            recent = values[-10:]
            trend = (recent[-1] - recent[0]) / len(recent)

            # Check for degradation patterns
            if "motor_current" in sensor_id and trend > 0.1:
                predictions.append(
                    PredictionResult(
                        metric=f"{sensor_id}_failure",
                        predicted_value=values[-1] * 1.5,
                        confidence=0.7,
                        horizon_hours=168,  # 1 week
                        timestamp=current_time,
                    )
                )

            if "bearing_temp" in sensor_id and trend > 0.05:
                predictions.append(
                    PredictionResult(
                        metric=f"{sensor_id}_overheat",
                        predicted_value=values[-1] + trend * 100,
                        confidence=0.65,
                        horizon_hours=72,
                        timestamp=current_time,
                    )
                )

        return predictions

    def detect_anomaly(
        self,
        sensor_id: str,
        value: float,
    ) -> Optional[str]:
        """Detect anomalous sensor readings."""
        if sensor_id not in self.sensor_history:
            self.sensor_history[sensor_id] = []

        history = self.sensor_history[sensor_id]
        history.append(value)

        # Keep last 100 readings
        if len(history) > 100:
            history.pop(0)

        if len(history) < 10:
            return None

        # Calculate statistics
        mean = sum(history) / len(history)
        variance = sum((x - mean) ** 2 for x in history) / len(history)
        std_dev = math.sqrt(variance) if variance > 0 else 1

        # Check for anomaly
        z_score = abs(value - mean) / std_dev if std_dev > 0 else 0
        if z_score > self.anomaly_threshold:
            return f"Anomaly detected: {sensor_id} = {value:.2f} (z-score: {z_score:.1f})"

        return None

    def optimize_parameters(
        self,
        current_params: dict[str, float],
        performance_history: list[dict],
    ) -> list[OptimizationSuggestion]:
        """Suggest parameter optimizations based on performance data."""
        suggestions = []

        if len(performance_history) < 5:
            return suggestions

        # Analyze recent performance
        recent = performance_history[-5:]
        avg_efficiency = sum(p.get("efficiency", 0) for p in recent) / len(recent)
        avg_energy = sum(p.get("energy_kwh", 0) for p in recent) / len(recent)

        # Temperature optimization
        if "reactor_temp" in current_params:
            current_temp = current_params["reactor_temp"]
            if avg_efficiency < 0.85:
                suggestions.append(
                    OptimizationSuggestion(
                        parameter="reactor_temp",
                        current_value=current_temp,
                        suggested_value=current_temp + 25,
                        expected_improvement=0.05,
                        reasoning="Increasing temperature may improve conversion efficiency",
                    )
                )
            elif avg_energy > 1.5:  # kWh/kg
                suggestions.append(
                    OptimizationSuggestion(
                        parameter="reactor_temp",
                        current_value=current_temp,
                        suggested_value=current_temp - 20,
                        expected_improvement=0.10,
                        reasoning="Reducing temperature may decrease energy consumption",
                    )
                )

        # Batch size optimization
        if "batch_size" in current_params:
            current_batch = current_params["batch_size"]
            if avg_efficiency < 0.80:
                suggestions.append(
                    OptimizationSuggestion(
                        parameter="batch_size",
                        current_value=current_batch,
                        suggested_value=current_batch * 0.8,
                        expected_improvement=0.03,
                        reasoning="Smaller batches may process more uniformly",
                    )
                )

        return suggestions


class DigitalTwin:
    """
    Complete Digital Twin for ARTEMIS-R system.

    Integrates:
    - Physical system model
    - Real-time sensor data
    - Physics simulation
    - AI/ML predictions
    - Visualization data export
    """

    def __init__(self, physical_system: Optional[ARTEMISSystem] = None):
        # Link to physical system (or create simulated one)
        self.physical = physical_system or ARTEMISSystem()
        self.controller = ARTEMISController()

        # Simulation engines
        self.physics = PhysicsEngine()
        self.ai = AIEngine()

        # State variables
        self.current_time = datetime.now()
        self.simulation_speed = 1.0  # Real-time multiplier

        # Data storage
        self.sensor_data: list[SensorData] = []
        self.predictions: list[PredictionResult] = []
        self.optimization_log: list[OptimizationSuggestion] = []

        # Virtual sensor states
        self.virtual_sensors = {
            "reactor_temp": 25.0,
            "reactor_pressure": 101.3,
            "extruder_zone1_temp": 25.0,
            "extruder_zone2_temp": 25.0,
            "extruder_zone3_temp": 25.0,
            "extruder_zone4_temp": 25.0,
            "press_upper_temp": 25.0,
            "press_lower_temp": 25.0,
            "shredder_motor_current": 0.0,
            "extruder_motor_current": 0.0,
            "hf_ppm": 0.0,
            "co_ppm": 0.0,
            "h2_percent": 0.0,
        }

        # Process variables
        self.reactor_mass_kg = 0.0
        self.heating_active = False

    def start_simulation(self) -> None:
        """Start digital twin simulation."""
        self.controller.start()
        self.physical.start()

    def stop_simulation(self) -> None:
        """Stop digital twin simulation."""
        self.controller.stop()
        self.physical.stop()

    def update(self, dt_seconds: float = 1.0) -> dict:
        """
        Update digital twin state.

        Args:
            dt_seconds: Time step in seconds

        Returns:
            Dictionary of updated values and events
        """
        events = []
        scaled_dt = dt_seconds * self.simulation_speed
        self.current_time += timedelta(seconds=scaled_dt)

        # Update physics simulation
        if self.heating_active:
            new_temp, energy = self.physics.simulate_reactor_thermal(
                self.virtual_sensors["reactor_temp"],
                self.controller.setpoints["reactor_temp"].value,
                self.reactor_mass_kg,
                800,  # Watts when heating
                scaled_dt,
            )
            self.virtual_sensors["reactor_temp"] = new_temp

        # Add sensor noise (realistic simulation)
        for sensor_id in self.virtual_sensors:
            # Safety-critical sensors (HF, CO) should not have noise that would cause false positives
            if sensor_id in ("hf_ppm", "co_ppm", "h2_percent"):
                # Gas sensors: only small noise around baseline (near-zero normally)
                noise = random.gauss(0, 0.001)
                self.virtual_sensors[sensor_id] = max(0, self.virtual_sensors[sensor_id] + noise)
            else:
                self.virtual_sensors[sensor_id] += random.gauss(0, 0.1)
                self.virtual_sensors[sensor_id] = max(0, self.virtual_sensors[sensor_id])

        # Record sensor data
        for sensor_id, value in self.virtual_sensors.items():
            self.sensor_data.append(
                SensorData(
                    timestamp=self.current_time,
                    sensor_id=sensor_id,
                    value=value,
                    unit=self._get_sensor_unit(sensor_id),
                )
            )

        # Update controller with sensor values
        self.controller.sensor_values = dict(self.virtual_sensors)
        self.controller.update(scaled_dt)

        # Run AI anomaly detection
        for sensor_id, value in self.virtual_sensors.items():
            anomaly = self.ai.detect_anomaly(sensor_id, value)
            if anomaly:
                events.append({"type": "anomaly", "message": anomaly})

        # Trim sensor history (keep last hour)
        cutoff = self.current_time - timedelta(hours=1)
        self.sensor_data = [s for s in self.sensor_data if s.timestamp > cutoff]

        return {
            "time": self.current_time.isoformat(),
            "sensors": dict(self.virtual_sensors),
            "events": events,
            "controller_status": self.controller.get_status(),
        }

    def _get_sensor_unit(self, sensor_id: str) -> str:
        """Get unit for sensor."""
        if "temp" in sensor_id:
            return "°C"
        elif "pressure" in sensor_id:
            return "kPa"
        elif "current" in sensor_id:
            return "A"
        elif "ppm" in sensor_id:
            return "ppm"
        elif "percent" in sensor_id:
            return "%"
        return ""

    def run_prediction(self) -> list[PredictionResult]:
        """Run predictive maintenance analysis."""
        sensor_history = {}
        for data in self.sensor_data:
            if data.sensor_id not in sensor_history:
                sensor_history[data.sensor_id] = []
            sensor_history[data.sensor_id].append(data.value)

        predictions = self.ai.predict_maintenance(sensor_history, self.current_time)
        self.predictions.extend(predictions)
        return predictions

    def get_optimization_suggestions(self) -> list[OptimizationSuggestion]:
        """Get AI-generated optimization suggestions."""
        current_params = {
            "reactor_temp": self.controller.setpoints["reactor_temp"].value,
            "batch_size": 3.0,
        }

        # Build performance history
        performance_history = []
        for event in self.physical.processing_history[-10:]:
            performance_history.append(
                {
                    "efficiency": event.output_mass_kg / event.input_mass_kg
                    if event.input_mass_kg > 0
                    else 0,
                    "energy_kwh": event.energy_kwh,
                }
            )

        suggestions = self.ai.optimize_parameters(current_params, performance_history)
        self.optimization_log.extend(suggestions)
        return suggestions

    def get_visualization_data(self) -> dict:
        """Get data formatted for visualization."""
        # Time series for charts
        time_series = {}
        for sensor_id in self.virtual_sensors:
            relevant_data = [s for s in self.sensor_data if s.sensor_id == sensor_id]
            time_series[sensor_id] = [
                {"time": s.timestamp.isoformat(), "value": s.value} for s in relevant_data[-100:]
            ]

        # Current values
        current = dict(self.virtual_sensors)

        # Module states
        modules = {
            "hopper": self.physical.hopper.get_status(),
            "thermal": self.physical.thermal.get_status(),
            "extruder": self.physical.extruder.get_status(),
            "shredder": self.physical.shredder.get_status(),
            "press": self.physical.press.get_status(),
        }

        # Metrics
        metrics = {
            "total_input_kg": self.physical.metrics.total_waste_input_kg,
            "total_products_kg": self.physical.metrics.total_products_kg,
            "mass_recovery": self.physical.metrics.mass_recovery_rate,
            "net_energy_kwh": self.physical.metrics.net_energy_kwh,
        }

        # Alarms
        alarms = [
            {
                "time": a.timestamp.isoformat(),
                "severity": a.severity.name,
                "source": a.source,
                "message": a.message,
            }
            for a in self.controller.active_alarms
        ]

        return {
            "timestamp": self.current_time.isoformat(),
            "time_series": time_series,
            "current": current,
            "modules": modules,
            "metrics": metrics,
            "alarms": alarms,
            "mode": self.controller.mode.name,
        }

    def export_state(self) -> str:
        """Export complete digital twin state as JSON."""
        state = {
            "version": "1.0",
            "system": "ARTEMIS-R Digital Twin",
            "timestamp": self.current_time.isoformat(),
            "visualization": self.get_visualization_data(),
            "physical_metrics": {
                "products": self.physical.get_product_summary(),
                "energy": self.physical.get_energy_summary(),
            },
            "predictions": [
                {
                    "metric": p.metric,
                    "value": p.predicted_value,
                    "confidence": p.confidence,
                    "horizon_hours": p.horizon_hours,
                }
                for p in self.predictions[-10:]
            ],
            "optimizations": [
                {
                    "parameter": o.parameter,
                    "current": o.current_value,
                    "suggested": o.suggested_value,
                    "improvement": o.expected_improvement,
                    "reasoning": o.reasoning,
                }
                for o in self.optimization_log[-5:]
            ],
        }
        return json.dumps(state, indent=2)

    def simulate_processing_day(self) -> dict:
        """Simulate a full day of processing."""
        from lunarecycle.waste.streams import WasteStream

        # Add daily waste
        items = WasteStream.get_all_items()
        waste_items = []
        waste_masses = []

        for item in items:
            daily_mass = item.daily_mass_4_crew
            if daily_mass > 0:
                waste_items.append(item)
                waste_masses.append(daily_mass)

        self.physical.add_waste(waste_items, waste_masses)

        # Enable heating
        self.heating_active = True
        self.reactor_mass_kg = sum(waste_masses)

        # Simulate 8 hours of processing (use 60-second steps for efficiency)
        for _ in range(8 * 60):  # 8 hours in minutes
            self.update(60.0)

        # Process all batches
        results = self.physical.process_all()

        # Run predictions and optimization
        predictions = self.run_prediction()
        suggestions = self.get_optimization_suggestions()

        return {
            "processing_results": {
                module: {
                    "input_kg": r.input_mass_kg,
                    "output_kg": r.total_product_mass,
                    "efficiency": r.efficiency,
                }
                for module, r in results.items()
            },
            "predictions": len(predictions),
            "suggestions": len(suggestions),
            "final_metrics": self.physical.get_product_summary(),
        }


def demo_digital_twin():
    """Demonstrate digital twin capabilities."""
    print("\n" + "=" * 70)
    print("ARTEMIS-R DIGITAL TWIN DEMONSTRATION")
    print("=" * 70)

    # Create digital twin
    twin = DigitalTwin()
    twin.start_simulation()

    print("\nSimulating 7 days of operation...")

    for day in range(7):
        print(f"\n--- Day {day + 1} ---")
        result = twin.simulate_processing_day()

        print(f"Processing events: {len(result['processing_results'])}")
        for module, data in result["processing_results"].items():
            print(f"  {module}: {data['input_kg']:.2f} kg -> {data['output_kg']:.2f} kg")

    # Final summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    viz = twin.get_visualization_data()
    print(f"\nTotal Input:    {viz['metrics']['total_input_kg']:.2f} kg")
    print(f"Total Products: {viz['metrics']['total_products_kg']:.2f} kg")
    print(f"Mass Recovery:  {viz['metrics']['mass_recovery']:.1%}")
    print(f"Net Energy:     {viz['metrics']['net_energy_kwh']:.2f} kWh")

    print(f"\nActive Alarms: {len(viz['alarms'])}")
    print(f"Operating Mode: {viz['mode']}")

    # Export state
    state_json = twin.export_state()
    print(f"\nState exported: {len(state_json)} bytes")

    return twin


if __name__ == "__main__":
    demo_digital_twin()
