
"""Boat simulation with linear drag, VPython UI and reusable controls."""

from __future__ import annotations

from pathlib import Path

from vpython import (
    arrow,
    box,
    button,
    canvas,
    color,
    compound,
    cylinder,
    gcurve,
    graph,
    menu,
    pyramid,
    rate,
    vector,
)

from common.vpython.cards import CardCenter
from common.vpython.parameter_panel import Parameter, ParameterPanel

from differential_equations.edo_physics_core import (
    DifferentialEquation,
    EulerSolver,
    RK4Solver,
    ODEState,
    SimulationEngine,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

PROBLEM_FILE = (
    BASE_DIR / "solutions" / "boat_problem_enunciation.tex"
)


# ============================================================
# DEFAULT PARAMETERS
# ============================================================

INITIAL_POSITION = 0.0
INITIAL_VELOCITY = 20.0

MASS = 1000.0
DRAG_COEFFICIENT = 700.0

DT = 0.01
FINAL_TIME = 20.0


# ============================================================
# DISPLAY SETTINGS
# ============================================================

CANVAS_W = 960
CANVAS_H = 540

GRAPH_W = 960
GRAPH_H = 250

FORCE_SCALE = 0.00092
VELOCITY_SCALE = 0.25
BOAT_FLOAT_Y = 1.4


# ============================================================
# DIFFERENTIAL EQUATION
# ============================================================

def boat_equation(
    t: float,
    y: tuple[float, ...],
    mass: float = MASS,
    drag: float = DRAG_COEFFICIENT,
) -> tuple[float, float]:
    """x' = v; v' = -(drag / mass) * v."""

    position, velocity = y

    return velocity, -(drag / mass) * velocity


# ============================================================
# ENGINE FACTORY
# ============================================================

def make_engine(
    *,
    position: float = INITIAL_POSITION,
    velocity: float = INITIAL_VELOCITY,
    mass: float = MASS,
    drag: float = DRAG_COEFFICIENT,
    dt: float = DT,
    method: str = "RK4",
) -> SimulationEngine:
    """Build a new independent solver for the boat scenario."""

    if mass <= 0 or dt <= 0 or drag < 0:
        raise ValueError(
            "Mass and time step must be positive; "
            "drag must be nonnegative."
        )

    ode = DifferentialEquation(
        derivative=lambda t, y: boat_equation(
            t, y, mass, drag
        ),
        initial_time=0.0,
        initial_state=(position, velocity),
    )

    solvers = {
        "Euler": EulerSolver,
        "RK4": RK4Solver,
    }

    if method not in solvers:
        raise ValueError(f"Unknown method: {method}")

    solver = solvers[method](
        ode=ode,
        step_size=dt,
    )

    return SimulationEngine(solver)


# ============================================================
# VPYTHON RENDERER
# ============================================================

class VPythonRenderer:
    """3D boat rendering and interactive interface."""

    def __init__(self, engine: SimulationEngine) -> None:

        self.engine = engine

        self.final_time = FINAL_TIME
        self.drag = DRAG_COEFFICIENT
        self.mass = MASS

        self.method = (
            "RK4"
            if isinstance(engine.solver, RK4Solver)
            else "Euler"
        )

        # Simulation state

        self.state = self._initial_state()
        self.is_running = False

        # Graph settings

        self.active_graph_view = "none"

        self.graphs: dict[str, object] = {}
        self.curves: dict[str, object] = {}

        # Camera settings

        self.camera_mode = "follow"

        # Initialize application

        self._setup_scene()
        self._save_camera_defaults()

        self.cards = CardCenter(
            pos=self.scene.caption_anchor,
            modal_pos=self.scene.title_anchor,
        )

        self._setup_ui_controls()
        self._setup_graphs()

        self._render_state(self.state)
        self._plot_state(self.state)

    def _initial_state(self) -> ODEState:
        """Create the initial numerical state."""

        ode = self.engine.solver.ode

        return ODEState(
            t=ode.initial_time,
            y=ode.initial_state,
        )

    @property
    def t(self) -> float:
        return self.state.t

    # ========================================================
    # SCENE
    # ========================================================

    def _setup_scene(self) -> None:
        """Create the 3D scene."""

        self.scene = canvas(
            align="left",
            width=CANVAS_W,
            height=CANVAS_H,
            background=vector(0.53, 0.81, 0.98),
            title="<h2>Boat — Linear Drag</h2>",
        )

        self.scene.center = vector(10, 2, 0)
        self.scene.range = 34
        self.scene.forward = vector(-0.7, -0.35, -1)

        # WATER
        WATER_W = 3000
        WATER_CHUNK_SZ = 30 

        for x in range(0, WATER_W, WATER_CHUNK_SZ):
            box(
                pos=vector(x - WATER_W/2 + WATER_CHUNK_SZ/2, 
                           0, 
                           0
                           ),
                size=vector(WATER_CHUNK_SZ, 0.6, WATER_CHUNK_SZ),
                opacity=0.5,
                texture="https://images.unsplash.com/photo-1568145675395-66a2eda0c6d7?q=80&w=735&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=NHwxMjA3fDA%3D"
            )

        # Boat model
        self._create_boat_model()

        # Force vectors
        self._setup_force_vectors()

    def _create_boat_model(self) -> None:
        """Create a more boat-like compound model."""

        x0 = self.state.y[0]

        # Hull
        hull = box(
            pos=vector(x0, BOAT_FLOAT_Y, 0),
            size=vector(7.5, 1.5, 3.2),
            color=vector(0.55, 0.18, 0.12),
        )

        # Bow (front tip)
        bow = pyramid(
            pos=vector(x0 + 4.2, BOAT_FLOAT_Y, 0),
            axis=vector(2.2, 0, 0),
            size=vector(2.2, 1.5, 3.0),
            color=vector(0.6, 0.2, 0.14),
        )

        # Cabin
        cabin = box(
            pos=vector(x0 - 0.7, BOAT_FLOAT_Y + 1.5, 0),
            size=vector(2.5, 1.3, 2.1),
            color=color.white,
        )

        # Mast
        mast = cylinder(
            pos=vector(x0 + 0.7, BOAT_FLOAT_Y + 0.8, 0),
            axis=vector(0, 3.1, 0),
            radius=0.08,
            color=color.white,
        )

        # Flag
        flag = box(
            pos=vector(x0 + 1.25, BOAT_FLOAT_Y + 3.2, 0),
            size=vector(1.0, 0.55, 0.06),
            color=color.yellow,
        )

        self.boat = compound(
            [hull, bow, cabin, mast, flag]
        )


    def _setup_force_vectors(self) -> None:
        """Create the displayed force vectors."""

        anchor = self.boat.pos + vector(0, 3.6, 0)

        self.drag_arrow = arrow(
            pos=anchor,
            axis=vector(0, 0, 0),
            shaftwidth=0.6,  
            headwidth=1.0,   
            headlength=0.8, 
            color=color.red,
            round=True,
        )

        self.velocity_arrow = arrow(
            pos=self.boat.pos + vector(0, 4.8, 0),
            axis=vector(0, 0, 0),
            shaftwidth=0.45,
            headwidth=0.9,
            headlength=0.8,
            color=color.cyan,
            round=True,
        )

        # self.weight_arrow = arrow(
        #     pos=anchor + vector(-1.1, 0, 0),
        #     axis=vector(0, -self.mass * 9.81 * FORCE_SCALE, 0),
        #     shaftwidth=0.18,
        #     color=color.yellow,
        # )

        # self.buoyancy_arrow = arrow(
        #     pos=anchor + vector(1.1, 0, 0),
        #     axis=vector(0, self.mass * 9.81 * FORCE_SCALE, 0),
        #     shaftwidth=0.18,
        #     color=color.green,
        # )


    def _update_force_vectors(self, velocity: float) -> None:
        """Update force vector positions and magnitudes."""

        anchor = self.boat.pos + vector(0, 3.6, 0)

        drag_force = -self.drag * velocity
        weight_force = self.mass * 9.81
        buoyancy_force = weight_force

        # DRAG FORCE
        self.drag_arrow.pos = anchor
        self._update_horizontal_arrow(
            self.drag_arrow,
            drag_force * FORCE_SCALE,
        )

        # # WEIGHT
        # self.weight_arrow.pos = (
        #     anchor + vector(-1.1, 0, 0)
        # )
        # self.weight_arrow.axis = vector(
        #     0, -weight_force * FORCE_SCALE, 0
        # )

        # # BUOYANCY
        # self.buoyancy_arrow.pos = (
        #     anchor + vector(1.1, 0, 0)
        # )
        # self.buoyancy_arrow.axis = vector(
        #     0, buoyancy_force * FORCE_SCALE, 0
        # )

        # VELOCITY
        self.velocity_arrow.pos = (
            self.boat.pos + vector(0, 4.8, 0)
        )

        self._update_horizontal_arrow(
            self.velocity_arrow,
            velocity * VELOCITY_SCALE,
        )
    
    @staticmethod
    def _update_horizontal_arrow(
        arrow_obj,
        signed_length: float,
    ) -> None:
        """Update arrow orientation and scale its head proportionally."""

        length = abs(signed_length)

        # Hide the vector when it becomes too small.
        if length < 0.05:
            arrow_obj.visible = False
            return

        arrow_obj.visible = True

        # Preserve the sign: negative points left.
        direction = 1 if signed_length > 0 else -1

        arrow_obj.axis = vector(
            direction * length,
            0,
            0,
        )

        # Keep the arrowhead proportional to its length.
        arrow_obj.headlength = min(0.8, length * 0.35)
        arrow_obj.headwidth = min(1.0, length * 0.5)


    # ========================================================
    # CAMERA
    # ========================================================

    def _save_camera_defaults(self) -> None:
        """Store initial camera settings."""

        self._camera_center = vector(
            self.scene.center.x,
            self.scene.center.y,
            self.scene.center.z,
        )

        self._camera_forward = vector(
            self.scene.forward.x,
            self.scene.forward.y,
            self.scene.forward.z,
        )

        self._camera_up = vector(
            self.scene.up.x,
            self.scene.up.y,
            self.scene.up.z,
        )

        self._camera_range = self.scene.range
        self._initial_boat_x = self.state.y[0]

    def _update_camera(self) -> None:
        """Follow the boat horizontally when tracking is enabled."""

        if self.camera_mode == "follow":
            self.scene.center = (
                self._camera_center
                + vector(
                    self.boat.pos.x - self._initial_boat_x -10,
                    0,
                    0,
                )
            )

    def _on_camera_change(self, selected_menu: menu) -> None:
        """Change the active camera mode."""

        self.camera_mode = (
            "follow"
            if selected_menu.selected == "Follow boat"
            else "fixed"
        )

        if self.camera_mode == "fixed":
            self.scene.center = vector(
                self._camera_center.x,
                self._camera_center.y,
                self._camera_center.z,
            )
        else:
            self._update_camera()

    def reset_camera(self, _event: object = None) -> None:
        """Restore camera position, orientation and zoom."""

        self.camera_mode = "follow"

        self.scene.center = vector(
            self._camera_center.x,
            self._camera_center.y,
            self._camera_center.z,
        )

        self.scene.forward = vector(
            self._camera_forward.x,
            self._camera_forward.y,
            self._camera_forward.z,
        )

        self.scene.up = vector(
            self._camera_up.x,
            self._camera_up.y,
            self._camera_up.z,
        )

        self.scene.range = self._camera_range

        self.camera_menu.selected = "Follow boat"

    # ========================================================
    # GRAPHS
    # ========================================================

    def _setup_graphs(self) -> None:
        """Rebuild graphs according to the current selection."""

        for chart in self.graphs.values():
            chart.delete()

        self.graphs.clear()
        self.curves.clear()

        # Position graph

        if self.active_graph_view in ("position", "all"):

            chart = graph(
                title="<b>Boat Position</b>",
                xtitle="Time (s)",
                ytitle="Position (m)",
                width=GRAPH_W,
                height=GRAPH_H,
                xmax=self.final_time,
            )

            self.graphs["position"] = chart

            self.curves["position"] = gcurve(
                graph=chart,
                color=color.orange,
            )

        # Velocity graph

        if self.active_graph_view in ("velocity", "all"):

            chart = graph(
                title="<b>Boat Velocity</b>",
                xtitle="Time (s)",
                ytitle="Velocity (m/s)",
                width=GRAPH_W,
                height=GRAPH_H,
                xmax=self.final_time,
            )

            self.graphs["velocity"] = chart

            self.curves["velocity"] = gcurve(
                graph=chart,
                color=color.cyan,
            )

    def _plot_state(self, state: ODEState) -> None:
        """Plot the state into active curves."""

        if "position" in self.curves:
            self.curves["position"].plot(
                state.t,
                state.y[0],
            )

        if "velocity" in self.curves:
            self.curves["velocity"].plot(
                state.t,
                state.y[1],
            )

    def _replot_history(self) -> None:
        """Reconstruct graphs from the current simulation history."""

        if not self.curves:
            return

        for state in self.engine.run(self.t):
            self._plot_state(state)

    def _on_graph_change(self, selected_menu: menu) -> None:
        """Handle graph menu selection."""

        mapping = {
            "NONE": "none",
            "Position": "position",
            "Velocity": "velocity",
            "ALL": "all",
        }

        view = mapping.get(selected_menu.selected)

        if view is None or view == self.active_graph_view:
            return

        self.active_graph_view = view

        self._setup_graphs()
        self._replot_history()

    # ========================================================
    # UI CONTROLS
    # ========================================================

    @staticmethod
    def _label(text: str) -> str:
        """Create compact labels for the right-hand column."""

        return (
            '<span style="'
            'display:inline-block;'
            'box-sizing:border-box;'
            'width:112px;'
            'margin-left:12px;'
            'vertical-align:middle;'
            'font:600 12px Arial,sans-serif;'
            'color:#475569">'
            f'{text}'
            '</span>'
        )

    def _setup_ui_controls(self) -> None:
        """Create simulation controls beside the 3D canvas."""

        caption = self.scene.append_to_caption
        anchor = self.scene.caption_anchor

        # Header

        caption(
            '<span style="'
            'display:inline-block;'
            'box-sizing:border-box;'
            'width:420px;'
            'margin:5px 0 5px 12px;'
            'padding:5px 0;'
            'border-bottom:1px solid #cbd5e1;'
            'font:700 15px Arial,sans-serif;'
            'color:#0f172a">'
            'SIMULATION'
            '</span><br>'
        )

        # Playback

        caption(self._label("Playback"))

        self.btn_pause = button(
            pos=anchor,
            text="▶ PLAY",
            bind=self.toggle_pause,
            background=color.green,
        )

        caption("&nbsp;")

        button(
            pos=anchor,
            text="RESTART",
            bind=self.restart_sim,
            background=color.cyan,
        )

        caption("<br>")

        # Numerical solver

        caption(self._label("Solver"))

        self.solver_menu = menu(
            pos=anchor,
            choices=["RK4", "Euler"],
            selected=self.method,
            bind=self._on_solver_change,
        )

        caption("<br>")

        # Graph selector

        caption(self._label("Graphs"))

        self.graph_menu = menu(
            pos=anchor,
            choices=[
                "NONE",
                "Position",
                "Velocity",
                "ALL",
            ],
            selected="NONE",
            bind=self._on_graph_change,
        )

        caption("<br>")

        # Problem statement

        self._setup_problem_statement_modal()

        caption("<br>")

        # Parameters

        self._setup_parameter_controls()

        # Keep subsequently created graphs below the controls.
        caption(
            '<div style="clear:both;height:0;line-height:0"></div>'
        )

    def _on_solver_change(self, widget: menu) -> None:
        """Choose solver; apply the choice with Apply Changes."""

        if widget.selected in ("RK4", "Euler"):
            self.method = widget.selected

    # ========================================================
    # PROBLEM STATEMENT
    # ========================================================

    def _setup_problem_statement_modal(self) -> None:
        """Register the problem statement popup."""

        try:
            content = PROBLEM_FILE.read_text(
                encoding="utf-8"
            )

            self.cards.add_modal_launcher(
                label="Problem",
                button_text="PROBLEM STATEMENT",
                title="Boat under linear drag",
                subtitle=(
                    "Variable Acceleration"
                ),
                content=content,
                latex=True,
                width="860px",
            )

        except (OSError, ValueError, RuntimeError) as exc:

            self.cards.add_modal_launcher(
                label="Problem",
                button_text="PROBLEM STATEMENT",
                title="Problem statement unavailable",
                content=str(exc),
                latex=False,
                width="640px",
            )

    # ========================================================
    # CAMERA CONTROLS
    # ========================================================

    def _setup_camera_controls(self) -> None:
        """Create camera controls inside the parameter panel."""

        caption = self.scene.append_to_caption
        anchor = self.scene.caption_anchor

        caption(
            '<span style="'
            'display:inline-block;'
            'box-sizing:border-box;'
            'width:420px;'
            'margin:5px 0 3px 12px;'
            'padding:3px 8px;'
            'border-left:3px solid #0d9488;'
            'background:#eaf3f5;'
            'color:#115e59;'
            'font:700 11px Arial,sans-serif">'
            'CAMERA'
            '</span><br>'
        )

        caption(self._label("Mode"))

        self.camera_menu = menu(
            pos=anchor,
            choices=[
                "Fixed (initial)",
                "Follow boat",
            ],
            selected="Follow boat",
            bind=self._on_camera_change,
        )

        caption("&nbsp;")

        button(
            pos=anchor,
            text="RESET CAMERA",
            bind=self.reset_camera,
            background=color.gray(0.85),
        )

        caption("<br>")

    # ========================================================
    # PARAMETER PANEL
    # ========================================================

    def _setup_parameter_controls(self) -> None:
        """Build the reusable numerical parameter panel."""

        start_x, start_v = (
            self.engine.solver.ode.initial_state
        )

        params = [
            # Initial conditions

            Parameter(
                name="position",
                label="Initial position (m)",
                value=start_x,
                group="Initial conditions",
                default=INITIAL_POSITION,
            ),

            Parameter(
                name="velocity",
                label="Initial velocity (m/s)",
                value=start_v,
                group="Initial conditions",
                default=INITIAL_VELOCITY,
            ),

            # Dynamics

            Parameter(
                name="mass",
                label="Mass (kg)",
                value=self.mass,
                minimum=1e-9,
                group="Dynamics",
                default=MASS,
            ),

            Parameter(
                name="drag",
                label="Drag coefficient (kg/s)",
                value=self.drag,
                minimum=0,
                group="Dynamics",
                default=DRAG_COEFFICIENT,
            ),

            # Numerical settings

            Parameter(
                name="dt",
                label="Time step (s)",
                value=self.engine.solver.step_size,
                minimum=0.001,
                group="Numerical settings",
                default=DT,
            ),

            Parameter(
                name="final_time",
                label="Final time (s)",
                value=self.final_time,
                minimum=0.01,
                group="Numerical settings",
                default=FINAL_TIME,
            ),
        ]

        self.parameter_panel = ParameterPanel(
            title="PARAMETERS",
            parameters=params,
            on_apply=self._apply_parameters,
            pos=self.scene.caption_anchor,
            extra_controls=self._setup_camera_controls,
        )

    def _apply_parameters(
        self,
        values: dict[str, float | int],
    ) -> None:
        """Rebuild the numerical simulation with new parameters."""

        # Validate and build first, then commit the changes.

        engine = make_engine(
            position=float(values["position"]),
            velocity=float(values["velocity"]),
            mass=float(values["mass"]),
            drag=float(values["drag"]),
            dt=float(values["dt"]),
            method=self.solver_menu.selected,
        )

        self.engine = engine

        self.mass = float(values["mass"])
        self.drag = float(values["drag"])
        self.final_time = float(values["final_time"])
        self.method = self.solver_menu.selected

        self.restart_sim(None)

    # ========================================================
    # PLAYBACK
    # ========================================================

    def _sync_play_button(self) -> None:
        """Update play button appearance."""

        self.btn_pause.text = (
            "⏸ PAUSE"
            if self.is_running
            else "▶ PLAY"
        )

        self.btn_pause.background = (
            color.orange
            if self.is_running
            else color.green
        )

    def toggle_pause(self, _event: object) -> None:
        """Start or pause numerical integration."""

        if self.t >= self.final_time:
            self.restart_sim(None)

        self.is_running = not self.is_running

        self._sync_play_button()

    def restart_sim(self, _event: object) -> None:
        """Restart simulation without changing the selected parameters."""

        self.is_running = False

        self.state = self._initial_state()
        self._initial_boat_x = self.state.y[0]

        self._sync_play_button()

        self._render_state(self.state)

        self._setup_graphs()
        self._plot_state(self.state)

    # ========================================================
    # RENDERING
    # ========================================================

    def _render_state(self, state: ODEState) -> None:
        """Update boat position, force vectors and camera."""

        position = state.y[0]
        velocity = state.y[1]

        self.boat.pos.x = position

        self._update_force_vectors(velocity)
        self._update_camera()

    # ========================================================
    # MAIN LOOP
    # ========================================================

    def run(self) -> None:
        """Integrate one numerical step per animation frame."""

        while True:

            rate(60)

            if not self.is_running:
                continue

            remaining = self.final_time - self.t

            if remaining <= 1e-12:
                self.is_running = False
                self._sync_play_button()
                continue

            step_size = min(
                self.engine.solver.step_size,
                remaining,
            )

            self.state = self.engine.solver.step(
                self.state,
                step_size,
            )

            self._render_state(self.state)
            self._plot_state(self.state)

            if self.t >= self.final_time - 1e-12:
                self.is_running = False
                self._sync_play_button()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    engine = make_engine()

    app = VPythonRenderer(engine)

    app.run()
