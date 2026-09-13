# vpython_app.py

from vpython import *

from differential_equations.first_order.edo1_physics_core import (
    DifferentialEquation,
    EulerSolver,
    RK4Solver,
    SimulationEngine,
)


# ============================================================
# Physical parameters
# ============================================================

INITIAL_POSITION = 0.0
INITIAL_VELOCITY = 20.0

DT = 0.01
FINAL_TIME = 20.0
MASS =  1000


# ============================================================
# Differential Equation
#
# x' = v
# v' = -(C/m)v
# ============================================================

def boat_equation(t, y):

    position = y[0]
    velocity = y[1]

    k = -70/MASS

    return (
        velocity,
        k * velocity
    )


# ============================================================
# Renderer
# ============================================================

class VPythonRenderer:

    def __init__(self, engine: SimulationEngine):

        self.engine = engine

        self.dt = DT
        self.t = 0.0

        self.is_running = True

        self._setup_scene()
        self._setup_graphs()
        self._setup_ui_controls()

    # --------------------------------------------------------
    # Scene
    # --------------------------------------------------------

    def _setup_scene(self):

        self.scene = canvas(
            align="left",
            width=650,
            height=400,
            background=vector(0.15, 0.15, 0.15),
            title="<h2>Boat — Linear Drag</h2>",
        )

        self.scene.center = vector(10, 30, -20)
        self.scene.range = 20
        self.scene.camera.axis = vector(0, -50, -30)

        self.water = box(
            pos=vector(0, 0, 0),
            size=vector(100, .6, 20),
            color=color.blue,
            opacity=0.5,
        )

        self.boat = box(
            pos=vector(INITIAL_POSITION, 0, 0),
            size=vector(8, 4, 2),
            color=color.red,
        )

    # --------------------------------------------------------
    # Graphs
    # --------------------------------------------------------

    def _setup_graphs(self):

        velocity_graph = graph(
            align="right",
            title="<b>Velocity</b>",
            width=650,
            height=250,
            xtitle="Time (s)",
            ytitle="Velocity (m/s)",
            xmax=FINAL_TIME,
        )

        self.velocity_curve = gcurve(
            graph=velocity_graph,
            color=color.cyan,
        )

        position_graph = graph(
            align="right",
            title="<b>Position</b>",
            width=650,
            height=250,
            xtitle="Time (s)",
            ytitle="Position (m)",
            xmax=FINAL_TIME,
        )

        self.position_curve = gcurve(
            graph=position_graph,
            color=color.orange,
        )

        self.all_curves = [
            self.velocity_curve,
            self.position_curve,
        ]

    # --------------------------------------------------------
    # Controls
    # --------------------------------------------------------

    def _setup_ui_controls(self):

        self.btn_pause = button(
            text="⏸ PAUSE",
            bind=self.toggle_pause,
            background=color.orange,
        )

        self.scene.append_to_caption("  ")

        button(
            text="🔄 RESTART",
            bind=self.restart_sim,
            background=color.blue,
        )

        self.scene.append_to_caption("\n<hr>")

    def toggle_pause(self, b):

        self.is_running = not self.is_running

        self.btn_pause.text = (
            "▶ PLAY"
            if not self.is_running
            else "⏸ PAUSE"
        )

        self.btn_pause.background = (
            color.green
            if not self.is_running
            else color.orange
        )

    def restart_sim(self, b):

        self.t = 0.0

        for curve in self.all_curves:
            curve.data = []

        self.boat.pos.x = INITIAL_POSITION

        if not self.is_running:
            self.toggle_pause(self.btn_pause)

    # --------------------------------------------------------
    # Rendering
    # --------------------------------------------------------

    def _plot_state(self, state):

        position = state.y[0]
        velocity = state.y[1]

        self.boat.pos.x = position

        self.position_curve.plot(
            state.t,
            position,
        )

        self.velocity_curve.plot(
            state.t,
            velocity,
        )

    # --------------------------------------------------------
    # Main loop
    # --------------------------------------------------------

    def run(self):

        while True:

            rate(60)

            if self.is_running:

                states = self.engine.run(self.t)

                state = states[-1]

                self._plot_state(state)

                self.t += self.dt

                if self.t > FINAL_TIME:
                    self.is_running = False


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # 1. Define the ODE
    # --------------------------------------------------------

    ode = DifferentialEquation(
        derivative=boat_equation,
        initial_time=0.0,
        initial_state=(
            INITIAL_POSITION,
            INITIAL_VELOCITY,
        ),
    )

    # --------------------------------------------------------
    # 2. Numerical method
    # --------------------------------------------------------

    solver = RK4Solver(
        ode=ode,
        step_size=DT,
    )

    # --------------------------------------------------------
    # 3. Simulation engine
    # --------------------------------------------------------

    engine = SimulationEngine(solver)

    # --------------------------------------------------------
    # 4. Presentation
    # --------------------------------------------------------

    app = VPythonRenderer(engine)

    app.run()