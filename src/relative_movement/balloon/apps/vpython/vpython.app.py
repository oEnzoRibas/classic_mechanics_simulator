"""VPython application: a rising balloon and a released cellphone.

Physics is provided by the generic relative_movement.physics_core module.
This file is responsible only for the scene, UI, graphs, and ground contact.
"""

from __future__ import annotations

from math import sqrt
from pathlib import Path
from typing import Optional

from vpython import (
    arrow,
    box,
    button,
    canvas,
    color,
    gcurve,
    graph,
    menu,
    rate,
    sphere,
    vec,
)

from common.vpython.cards import CardCenter
from common.vpython.parameter_panel import Parameter, ParameterPanel
from relative_movement.physics_core import GRAVITY, PointMass, SimulationEngine

BASE_DIR = Path(__file__).resolve().parent
ANALYTICAL_SOLUTION_FILE = (
    BASE_DIR / "solutions" / "ballon_problem_enunciation.tex"
)

GRAPH_W = 650
GRAPH_H = 200
GRAPH_XMAX = 2.8
GRAPH_SCALE = 1.5
VELOCITY_ARROW_SCALE = 0.9
CANVAS_H = 600
CANVAS_W = 520

# Physical defaults belong to this scenario, not the general-purpose engine.
DEFAULT_CELL_MASS = 1.0
DEFAULT_CELL_Y = 10.0
DEFAULT_CELL_V = 10.0
DEFAULT_BALLOON_MASS = 1.0
DEFAULT_BALLOON_Y = 10.0
DEFAULT_BALLOON_V = 10.0


class VPythonRenderer:
    """Present a two-body example and graph the engine's snapshots."""

    def __init__(self, engine: SimulationEngine) -> None:
        if not {"cellphone", "balloon"}.issubset(engine.objects):
            raise ValueError("The balloon application needs cellphone and balloon.")

        self.engine = engine
        self.dt = 0.01
        self.t = 0.0
        self.is_running = False
        self.has_landed = False
        self.active_ref = "ground"
        self.active_graph_view = "pos"
        self.graphs: dict[str, object] = {}
        self.curves: dict[str, object] = {}

        self._setup_scene()
        self.cards = CardCenter(pos=self.scene.caption_anchor)
        self._setup_graphs()
        self._setup_ui_controls()

        first = self.engine.get_snapshot(0.0, self.active_ref)
        self._update_visuals(first)
        self._plot_graphs(0.0, first)

    # ---- VPython scene -------------------------------------------------

    def _setup_scene(self) -> None:
        self.scene = canvas(
            align="left",
            width=CANVAS_W,
            height=CANVAS_H,
            background=vec(0.0, 0.08, 0.2),
            title="<h2>Kinematics &amp; Reference Frames</h2>",
        )
        self.scene.center = vec(0, 10, 30)
        self.scene.range = 25
        self.meshes = {
            "ground": box(
                pos=vec(0, 0, 0),
                size=vec(30, 0.2, 30),
                color=color.gray(0.5),
            ),
            "balloon": sphere(
                pos=vec(-2, 10, 3), radius=1.2, color=color.cyan
            ),
            "cellphone": box(
                pos=vec(2, 10, 3), size=vec(2, 2, 2), color=color.red
            ),
        }
        self.velocity_arrows = {
            "cellphone": arrow(
                pos=self.meshes["cellphone"].pos,
                axis=vec(0, 0, 0),
                color=color.green,
                shaftwidth=0.95,
                round=True,
            ),
            "balloon": arrow(
                pos=self.meshes["balloon"].pos,
                axis=vec(0, 0, 0),
                color=color.yellow,
                shaftwidth=0.95,
                round=True,
            ),
        }

    @property
    def contact_y(self) -> float:
        """Cellphone-center height when the bottom touches the ground top."""
        ground = self.meshes["ground"]
        cellphone = self.meshes["cellphone"]
        return ground.pos.y + ground.size.y / 2 + cellphone.size.y / 2

    # ---- Graphs --------------------------------------------------------

    def _setup_graphs(self) -> None:
        for old_graph in self.graphs.values():
            old_graph.delete()
        self.graphs.clear()
        self.curves.clear()

        show_position = self.active_graph_view in ("all", "pos")
        show_cell_energy = self.active_graph_view in ("all", "cell_eng")
        show_balloon_energy = self.active_graph_view in ("all", "balloon_eng")
        scale = 1 if self.active_graph_view == "all" else GRAPH_SCALE
        width, height = int(GRAPH_W * scale), int(GRAPH_H * scale)

        if show_position:
            chart = graph(
                align="right",
                title="<b>Relative Position (m)</b>",
                xtitle="Time (s)",
                ytitle="Position (m)",
                width=width,
                height=height,
                xmax=GRAPH_XMAX,
            )
            self.graphs["pos"] = chart
            self.curves["c_pos"] = gcurve(
                graph=chart, color=color.red, label="Cellphone"
            )
            self.curves["b_pos"] = gcurve(
                graph=chart, color=color.cyan, label="Balloon"
            )

        if show_cell_energy:
            chart = graph(
                align="right",
                title="<b>Cellphone Energy (J)</b>",
                xtitle="Time (s)",
                ytitle="Energy (J)",
                width=width,
                height=height,
                xmax=GRAPH_XMAX,
            )
            self.graphs["cell_eng"] = chart
            self.curves["c_K"] = gcurve(
                graph=chart, color=color.blue, label="Kinetic (K)"
            )
            self.curves["c_U"] = gcurve(
                graph=chart, color=color.orange, label="Potential (U)"
            )
            self.curves["c_E"] = gcurve(
                graph=chart, color=color.red, label="Mechanical (E)"
            )

        if show_balloon_energy:
            chart = graph(
                align="right",
                title="<b>Balloon Energy (J)</b>",
                xtitle="Time (s)",
                ytitle="Energy (J)",
                width=width,
                height=height,
                xmax=GRAPH_XMAX,
            )
            self.graphs["balloon_eng"] = chart
            self.curves["b_K"] = gcurve(
                graph=chart, color=color.blue, label="Kinetic (K)"
            )
            self.curves["b_U"] = gcurve(
                graph=chart, color=color.orange, label="Potential (U)"
            )
            self.curves["b_E"] = gcurve(
                graph=chart, color=color.cyan, label="Mechanical (E)"
            )

    def _plot_graphs(self, current_time: float, snapshot: dict) -> None:
        cellphone, balloon = snapshot["cellphone"], snapshot["balloon"]
        values = {
            "c_pos": cellphone["rel_y"],
            "b_pos": balloon["rel_y"],
            "c_K": cellphone["energies"].kinetic,
            "c_U": cellphone["energies"].potential,
            "c_E": cellphone["energies"].mechanical,
            "b_K": balloon["energies"].kinetic,
            "b_U": balloon["energies"].potential,
            "b_E": balloon["energies"].mechanical,
        }
        for name, curve in self.curves.items():
            curve.plot(current_time, values[name])

    def _replot_history(self) -> None:
        """Rebuild the graph using the current frame, including contact time."""
        last_sample = -1.0
        for index in range(int(self.t / self.dt) + 1):
            sample_t = index * self.dt
            snapshot = self.engine.get_snapshot(sample_t, self.active_ref)
            self._plot_graphs(sample_t, snapshot)
            last_sample = sample_t
        if self.t - last_sample > 1e-9:
            self._plot_graphs(
                self.t, self.engine.get_snapshot(self.t, self.active_ref)
            )

    # ---- UI ------------------------------------------------------------

    def _setup_ui_controls(self) -> None:
        self.btn_pause = button(
            pos=self.scene.caption_anchor,
            text="▶ PLAY", bind=self.toggle_pause, background=color.green
        )
        self.scene.append_to_caption("  ")
        button(
            pos=self.scene.caption_anchor,
            text="🔄 RESTART", bind=self.restart_sim, background=color.blue
        )
        self.scene.append_to_caption("\n<b>Active Reference:</b> &nbsp;&nbsp;")

        self.btn_ground = button(
            pos=self.scene.caption_anchor,
            text="◉ GROUND", bind=lambda _: self.change_ref("ground"),
            background=color.green,
        )
        self.scene.append_to_caption("  ")
        self.btn_cell = button(
            pos=self.scene.caption_anchor,
            text="○ CELLPHONE", bind=lambda _: self.change_ref("cellphone"),
            background=color.gray(0.5),
        )
        self.scene.append_to_caption("  ")
        self.btn_balloon = button(
            pos=self.scene.caption_anchor,
            text="○ BALLOON", bind=lambda _: self.change_ref("balloon"),
            background=color.gray(0.5),
        )

        self.scene.append_to_caption("\n<b>Display Graphs:</b> &nbsp;&nbsp;")
        self.menu_graphs = menu(
            pos=self.scene.caption_anchor,
            choices=["ALL", "Position", "Cellphone Energy", "Balloon Energy"],
            selected="Position",
            bind=self._on_graph_menu_change,
        )
        self.scene.append_to_caption("\n<hr>")
        button(
            pos=self.scene.caption_anchor,
            text="📐 SOLUÇÃO ANALÍTICA",
            bind=self.show_analytical_solution,
            background=color.cyan,
        )
        self.scene.append_to_caption("\n<hr>")
        self._setup_parameter_controls()

    def _setup_parameter_controls(self) -> None:
        cell = self.engine.objects["cellphone"]
        balloon = self.engine.objects["balloon"]
        params = [
            Parameter(
                "gravity", "Gravidade (m/s²)", self.engine.gravity,
                minimum=0, group="Ambiente", default=GRAVITY,
            ),
            Parameter(
                "cell_mass", "Massa (kg)", cell.mass,
                minimum=1e-9, group="Celular", default=DEFAULT_CELL_MASS,
            ),
            Parameter(
                "cell_y", "Posição inicial (m)", cell.initial_y,
                minimum=self.contact_y, group="Celular", default=DEFAULT_CELL_Y,
            ),
            Parameter(
                "cell_v", "Velocidade inicial (m/s)", cell.initial_v,
                group="Celular", default=DEFAULT_CELL_V,
            ),
            Parameter(
                "balloon_mass", "Massa (kg)", balloon.mass,
                minimum=1e-9, group="Balão", default=DEFAULT_BALLOON_MASS,
            ),
            Parameter(
                "balloon_y", "Posição inicial (m)", balloon.initial_y,
                group="Balão", default=DEFAULT_BALLOON_Y,
            ),
            Parameter(
                "balloon_v", "Velocidade inicial (m/s)", balloon.initial_v,
                group="Balão", default=DEFAULT_BALLOON_V,
            ),
        ]
        self.parameter_panel = ParameterPanel(
            title="⚙ Central de Controle",
            parameters=params,
            on_apply=self._apply_parameters,
            pos=self.scene.caption_anchor,
        )

    def _apply_parameters(self, values: dict[str, float | int]) -> None:
        """Called after ParameterPanel has validated all numeric fields."""
        if values["cell_y"] <= self.contact_y:
            raise ValueError("O celular deve começar acima do chão.")

        cellphone = PointMass(
            name="cellphone", mass=values["cell_mass"],
            initial_y=values["cell_y"], initial_v=values["cell_v"],
            accel=-values["gravity"],
        )
        balloon = PointMass(
            name="balloon", mass=values["balloon_mass"],
            initial_y=values["balloon_y"], initial_v=values["balloon_v"],
            accel=0.0,
        )
        self.engine = SimulationEngine(
            objects={"cellphone": cellphone, "balloon": balloon},
            gravity=values["gravity"],
        )
        self.restart_sim(None)

    def _on_graph_menu_change(self, selected_menu: menu) -> None:
        selected = selected_menu.selected
        selection = {
            "ALL": "all",
            "Position": "pos",
            "Cellphone Energy": "cell_eng",
            "Balloon Energy": "balloon_eng",
        }
        if selected in selection:
            self.set_graph_view(selection[selected])

    def set_graph_view(self, view_mode: str) -> None:
        if view_mode not in {"all", "pos", "cell_eng", "balloon_eng"}:
            raise ValueError(f"Unknown graph view: {view_mode}")
        if view_mode == self.active_graph_view:
            return
        self.active_graph_view = view_mode
        self._setup_graphs()
        self._replot_history()

    def _sync_play_button(self) -> None:
        self.btn_pause.text = "⏸ PAUSE" if self.is_running else "▶ PLAY"
        self.btn_pause.background = (
            color.orange if self.is_running else color.green
        )

    def toggle_pause(self, _button: object) -> None:
        if self.has_landed and not self.is_running:
            self.restart_sim(None)
        self.is_running = not self.is_running
        self._sync_play_button()

    def restart_sim(self, _button: object) -> None:
        self.t = 0.0
        self.is_running = False
        self.has_landed = False
        self._sync_play_button()
        self._setup_graphs()
        initial = self.engine.get_snapshot(0.0, self.active_ref)
        self._update_visuals(initial)
        self._plot_graphs(0.0, initial)

    def change_ref(self, selected_ref: str) -> None:
        if selected_ref not in self.engine.reference_frames:
            raise ValueError(f"Unknown reference frame: {selected_ref}")
        self.active_ref = selected_ref
        for ref, widget in (
            ("ground", self.btn_ground),
            ("cellphone", self.btn_cell),
            ("balloon", self.btn_balloon),
        ):
            active = selected_ref == ref
            widget.text = ("◉ " if active else "○ ") + ref.upper()
            widget.background = color.green if active else color.gray(0.5)

        # Important: update the arrows NOW, even when simulation is paused.
        snapshot = self.engine.get_snapshot(self.t, self.active_ref)
        self._update_visuals(snapshot)
        if self.has_landed:
            self._set_cellphone_at_contact()
        self._setup_graphs()
        self._replot_history()

    def show_analytical_solution(self, _button: object) -> None:
        if self.is_running:
            self.is_running = False
            self._sync_play_button()
        try:
            latex_source = ANALYTICAL_SOLUTION_FILE.read_text(encoding="utf-8")
            self.cards.open_card(
                title="Solução Analítica",
                subtitle="Resolução matemática do problema",
                content=latex_source,
                latex=True,
                width="640px",
            )
        except (OSError, RuntimeError, ValueError) as exc:
            self.cards.open_card(
                title="Solução Analítica — erro",
                content=f"Não foi possível mostrar a solução: {exc}",
            )

    # ---- Render and impact ---------------------------------------------

    def _update_visuals(self, snapshot: dict) -> None:
        for name in ("cellphone", "balloon"):
            mesh = self.meshes[name]
            mesh.pos.y = snapshot[name]["abs_y"]
            self.velocity_arrows[name].pos = mesh.pos
            self.velocity_arrows[name].axis = vec(
                0, snapshot[name]["rel_v"] * VELOCITY_ARROW_SCALE, 0
            )

    def _set_cellphone_at_contact(self) -> None:
        self.meshes["cellphone"].pos.y = self.contact_y
        self.velocity_arrows["cellphone"].pos = self.meshes["cellphone"].pos

    def _impact_time(self) -> Optional[float]:
        """Exact time of the FIRST descending contact with the ground."""
        cell = self.engine.objects["cellphone"]
        y0, v0, a = cell.initial_y, cell.initial_v, cell.accel
        gap = y0 - self.contact_y
        if gap <= 0:
            return 0.0
        if abs(a) < 1e-14:
            return -gap / v0 if v0 < 0 else None
        discriminant = v0 * v0 - 2 * a * gap
        if discriminant < 0:
            return None
        root = sqrt(discriminant)
        candidates = [(-v0 - root) / a, (-v0 + root) / a]
        descending = [
            time for time in candidates
            if time >= 0 and v0 + a * time < 0
        ]
        return min(descending) if descending else None

    def run(self) -> None:
        """Advance time and stop exactly at the first ground impact."""
        while True:
            rate(60)
            if not self.is_running:
                continue

            next_t = self.t + self.dt
            impact = self._impact_time()
            hit = impact is not None and impact <= next_t + 1e-12

            self.t = max(self.t, impact) if hit else next_t
            snapshot = self.engine.get_snapshot(self.t, self.active_ref)
            self._update_visuals(snapshot)
            if hit:
                self._set_cellphone_at_contact()
            self._plot_graphs(self.t, snapshot)

            if hit:
                self.has_landed = True
                self.is_running = False
                self._sync_play_button()


def make_default_engine() -> SimulationEngine:
    """Initial configuration for this example; not part of the physics core."""
    return SimulationEngine(
        objects={
            "cellphone": PointMass(
                "cellphone", DEFAULT_CELL_MASS, DEFAULT_CELL_Y,
                DEFAULT_CELL_V, -GRAVITY,
            ),
            "balloon": PointMass(
                "balloon", DEFAULT_BALLOON_MASS, DEFAULT_BALLOON_Y,
                DEFAULT_BALLOON_V, 0.0,
            ),
        },
        gravity=GRAVITY,
    )


if __name__ == "__main__":
    VPythonRenderer(make_default_engine()).run()
