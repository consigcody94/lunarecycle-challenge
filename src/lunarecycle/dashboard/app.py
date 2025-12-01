"""
ARTEMIS-R Dashboard Application

Simple web-based dashboard for monitoring the ARTEMIS-R digital twin.
Run with: python -m lunarecycle.dashboard.app
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

# Check if dash is available
try:
    from dash import Dash, html, dcc, callback, Output, Input
    import plotly.graph_objects as go
    import plotly.express as px

    DASH_AVAILABLE = True
except ImportError:
    DASH_AVAILABLE = False
    print("Note: Dash not installed. Install with: pip install dash plotly")

from lunarecycle.artemis.digital_twin import DigitalTwin
from lunarecycle.artemis.system import run_artemis_simulation


def create_dashboard():
    """Create the ARTEMIS-R monitoring dashboard."""
    if not DASH_AVAILABLE:
        print("Dashboard requires dash and plotly. Install with:")
        print("  pip install dash plotly")
        return None

    # Initialize digital twin
    twin = DigitalTwin()
    twin.start_simulation()

    # Run initial simulation
    for _ in range(7):
        twin.simulate_processing_day()

    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.H1("ARTEMIS-R Digital Twin Dashboard", style={"textAlign": "center"}),
            html.Div(
                [
                    html.Div(
                        [
                            html.H3("System Status"),
                            html.Div(id="status-display"),
                        ],
                        style={"width": "30%", "display": "inline-block", "verticalAlign": "top"},
                    ),
                    html.Div(
                        [
                            html.H3("Mass Flow"),
                            dcc.Graph(id="mass-chart"),
                        ],
                        style={"width": "35%", "display": "inline-block"},
                    ),
                    html.Div(
                        [
                            html.H3("Energy Balance"),
                            dcc.Graph(id="energy-chart"),
                        ],
                        style={"width": "35%", "display": "inline-block"},
                    ),
                ]
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H3("Product Breakdown"),
                            dcc.Graph(id="products-chart"),
                        ],
                        style={"width": "50%", "display": "inline-block"},
                    ),
                    html.Div(
                        [
                            html.H3("Temperature Trends"),
                            dcc.Graph(id="temp-chart"),
                        ],
                        style={"width": "50%", "display": "inline-block"},
                    ),
                ]
            ),
            dcc.Interval(id="interval-component", interval=5000, n_intervals=0),  # 5 second updates
            dcc.Store(id="twin-data"),
        ]
    )

    @callback(Output("twin-data", "data"), Input("interval-component", "n_intervals"))
    def update_data(n):
        viz = twin.get_visualization_data()
        return json.dumps(viz)

    @callback(Output("status-display", "children"), Input("twin-data", "data"))
    def update_status(data):
        if not data:
            return "Loading..."
        viz = json.loads(data)
        metrics = viz.get("metrics", {})

        return html.Div(
            [
                html.P(f"Mode: {viz.get('mode', 'Unknown')}"),
                html.P(f"Total Input: {metrics.get('total_input_kg', 0):.1f} kg"),
                html.P(f"Total Products: {metrics.get('total_products_kg', 0):.1f} kg"),
                html.P(f"Mass Recovery: {metrics.get('mass_recovery', 0):.1%}"),
                html.P(f"Net Energy: {metrics.get('net_energy_kwh', 0):.1f} kWh"),
                html.P(f"Active Alarms: {len(viz.get('alarms', []))}"),
            ]
        )

    @callback(Output("mass-chart", "figure"), Input("twin-data", "data"))
    def update_mass_chart(data):
        if not data:
            return go.Figure()
        viz = json.loads(data)
        metrics = viz.get("metrics", {})

        fig = go.Figure(
            data=[
                go.Bar(
                    x=["Input", "Products", "Residue"],
                    y=[
                        metrics.get("total_input_kg", 0),
                        metrics.get("total_products_kg", 0),
                        metrics.get("total_input_kg", 0) - metrics.get("total_products_kg", 0),
                    ],
                    marker_color=["blue", "green", "red"],
                )
            ]
        )
        fig.update_layout(title="Mass Balance (kg)", yaxis_title="Mass (kg)")
        return fig

    @callback(Output("energy-chart", "figure"), Input("twin-data", "data"))
    def update_energy_chart(data):
        if not data:
            return go.Figure()
        viz = json.loads(data)

        # Get from physical system
        products = twin.physical.get_energy_summary()

        fig = go.Figure(
            data=[
                go.Bar(
                    x=["Consumed", "Recovered", "Net"],
                    y=[
                        products.get("consumed_kwh", 0),
                        products.get("recovered_kwh", 0),
                        products.get("net_kwh", 0),
                    ],
                    marker_color=["red", "green", "blue"],
                )
            ]
        )
        fig.update_layout(title="Energy Balance (kWh)", yaxis_title="Energy (kWh)")
        return fig

    @callback(Output("products-chart", "figure"), Input("twin-data", "data"))
    def update_products_chart(data):
        if not data:
            return go.Figure()

        products = twin.physical.get_product_summary()

        labels = []
        values = []
        for name, mass in products.items():
            if name != "total_kg" and mass > 0:
                labels.append(name.replace("_kg", "").replace("_", " ").title())
                values.append(mass)

        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        fig.update_layout(title="Product Distribution")
        return fig

    @callback(Output("temp-chart", "figure"), Input("twin-data", "data"))
    def update_temp_chart(data):
        if not data:
            return go.Figure()
        viz = json.loads(data)
        current = viz.get("current", {})

        temps = {
            "Reactor": current.get("reactor_temp", 0),
            "Extruder Z1": current.get("extruder_zone1_temp", 0),
            "Extruder Z2": current.get("extruder_zone2_temp", 0),
            "Extruder Z3": current.get("extruder_zone3_temp", 0),
            "Extruder Z4": current.get("extruder_zone4_temp", 0),
            "Press Upper": current.get("press_upper_temp", 0),
            "Press Lower": current.get("press_lower_temp", 0),
        }

        fig = go.Figure(data=[go.Bar(x=list(temps.keys()), y=list(temps.values()))])
        fig.update_layout(title="Current Temperatures", yaxis_title="Temperature (°C)")
        return fig

    return app


def run_dashboard(host: str = "127.0.0.1", port: int = 8050, debug: bool = True):
    """Run the dashboard server."""
    app = create_dashboard()
    if app:
        print(f"\nStarting ARTEMIS-R Dashboard at http://{host}:{port}")
        app.run(host=host, port=port, debug=debug)
    else:
        print("Could not start dashboard. Missing dependencies.")


# Alternative: Text-based dashboard for environments without GUI
def print_dashboard():
    """Print a text-based dashboard to console."""
    print("\n" + "=" * 70)
    print("ARTEMIS-R DIGITAL TWIN - CONSOLE DASHBOARD")
    print("=" * 70)

    # Run simulation
    twin = DigitalTwin()
    twin.start_simulation()

    print("\nSimulating 7 days of operation...")
    for day in range(7):
        result = twin.simulate_processing_day()
        print(f"Day {day + 1}: {len(result['processing_results'])} processing events")

    # Get final data
    viz = twin.get_visualization_data()
    products = twin.physical.get_product_summary()
    energy = twin.physical.get_energy_summary()

    print("\n" + "-" * 70)
    print("SYSTEM STATUS")
    print("-" * 70)
    print(f"Operating Mode: {viz['mode']}")
    print(f"Active Alarms: {len(viz['alarms'])}")

    print("\n" + "-" * 70)
    print("MASS BALANCE")
    print("-" * 70)
    metrics = viz["metrics"]
    print(f"Total Input:     {metrics['total_input_kg']:.2f} kg")
    print(f"Total Products:  {metrics['total_products_kg']:.2f} kg")
    print(f"Mass Recovery:   {metrics['mass_recovery']:.1%}")

    print("\n" + "-" * 70)
    print("PRODUCTS")
    print("-" * 70)
    for name, mass in products.items():
        if name != "total_kg" and mass > 0:
            label = name.replace("_kg", "").replace("_", " ").title()
            print(f"  {label}: {mass:.2f} kg")

    print("\n" + "-" * 70)
    print("ENERGY BALANCE")
    print("-" * 70)
    print(f"Consumed:  {energy['consumed_kwh']:.2f} kWh")
    print(f"Recovered: {energy['recovered_kwh']:.2f} kWh")
    print(f"Net:       {energy['net_kwh']:.2f} kWh")
    status = "ENERGY POSITIVE" if energy["net_kwh"] > 0 else "ENERGY NEGATIVE"
    print(f"Status:    {status}")

    print("\n" + "-" * 70)
    print("SENSOR VALUES")
    print("-" * 70)
    current = viz["current"]
    for sensor, value in sorted(current.items()):
        if "temp" in sensor:
            print(f"  {sensor}: {value:.1f} °C")
        elif "pressure" in sensor:
            print(f"  {sensor}: {value:.1f} kPa")
        elif "ppm" in sensor:
            print(f"  {sensor}: {value:.2f} ppm")

    print("\n" + "=" * 70)
    print("Dashboard complete. For web interface, install: pip install dash plotly")
    print("=" * 70)

    return twin


if __name__ == "__main__":
    import sys

    if "--web" in sys.argv and DASH_AVAILABLE:
        run_dashboard()
    else:
        print_dashboard()
