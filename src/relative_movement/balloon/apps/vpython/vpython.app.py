from vpython import *
from relative_movement.balloon.physics_core import PointMass, SimulationEngine, GRAVITY
from typing import Dict, List, Optional

# --- UI Constants ---
GRAPH_W = 650
GRAPH_H = 200
GRAPH_XMAX = 2.8

class VPythonRenderer:
    """
    Presentation layer responsible for rendering the 3D scene and graphs.
    It acts as a consumer of the SimulationEngine.
    """
    def __init__(self, engine: SimulationEngine):
        self.engine = engine
        self.dt = 0.01
        self.t = 0.0
        self.is_running = True
        self.active_ref = "ground"
        self.refs = ["ground", "cellphone", "balloon"]
        self.active_graph_view = "pos"

        self.graphs: Dict[str, graph] = {}
        self.curves: Dict[str, gcurve] = {}
        self.all_curves: List[gcurve] = []

        self._setup_scene()
        self._setup_graphs()
        self._setup_ui_controls()
        
    def _setup_scene(self) -> None:
        """Initializes the VPython 3D canvas and meshes."""
        self.scene = canvas(
            align="left",
            width=520, height=600,
            background=vector(0.15, 0.15, 0.15),
            title="<h2>Kinematics & Reference Frames</h2>"
        )
        self.scene.center = vec(0, 20, 30)
        self.scene.range = 10
        
        # 3D Objects mapping
        self.meshes = {
            "ground": box(
                pos=vec(0, 0, 0), 
                size=vec(30, 0.2, 30), 
                color=color.gray(0.5)
                ),
            "balloon": sphere(
                pos=vec(-2, 10, 3), 
                radius=1.2, 
                color=color.cyan
                ),
            "cellphone": box(
                pos=vec(2, 10, 3), 
                size=vec(2, 2, 2), 
                color=color.red
                )
        }
        
    def _setup_graphs(self) -> None:
        """
        Lifecycle management for graph widgets.
        Destroys existing canvases and instantiates only active graphs.
        """

        for g in self.graphs.values():
            g.delete()

        self.graphs.clear()
        self.curves.clear()
        self.all_curves.clear()
        
        show_pos = self.active_graph_view in ("all", "pos")
        show_cell = self.active_graph_view in ("all", "cell_eng")
        show_balloon = self.active_graph_view in ("all", "balloon_eng")

        if show_pos:
            
            g_pos = graph(
                align="right",
                title="<b>Relative Position (m)</b>",
                width=GRAPH_W,
                height=GRAPH_H,
                xmax=GRAPH_XMAX,
            )
            
            self.graphs["pos"] = g_pos
            
            self.curves["c_pos"] = gcurve(
                graph=g_pos, color=color.red, label="Cellphone"
            )
            
            self.curves["b_pos"] = gcurve(
                graph=g_pos, color=color.cyan, label="Balloon"
            )
            
            self.all_curves.extend([self.curves["c_pos"], self.curves["b_pos"]])

        if show_cell:
            
            g_c_eng = graph(
                align="right",
                title="<b>Cellphone Energy (J)</b>",
                width=GRAPH_W,
                height=GRAPH_H,
                xmax=GRAPH_XMAX,
            )

            self.graphs["cell_eng"] = g_c_eng
            self.curves["c_K"] = gcurve(
                graph=g_c_eng, color=color.blue, label="Kinetic (K)"
            )
            self.curves["c_U"] = gcurve(
                graph=g_c_eng, color=color.orange, label="Potential (U)"
            )
            self.curves["c_E"] = gcurve(
                graph=g_c_eng, color=color.red, label="Mechanical (E)"
            )
            self.all_curves.extend(
                [self.curves["c_K"], self.curves["c_U"], self.curves["c_E"]]
            )

        if show_balloon:
            g_b_eng = graph(
                align="right",
                title="<b>Balloon Energy (J)</b>",
                width=GRAPH_W,
                height=GRAPH_H,
                xmax=GRAPH_XMAX,
            )
            self.graphs["balloon_eng"] = g_b_eng
            self.curves["b_K"] = gcurve(
                graph=g_b_eng, color=color.blue, label="Kinetic (K)"
            )
            self.curves["b_U"] = gcurve(
                graph=g_b_eng, color=color.orange, label="Potential (U)"
            )
            self.curves["b_E"] = gcurve(
                graph=g_b_eng, color=color.cyan, label="Mechanical (E)"
            )
            self.all_curves.extend(
                [self.curves["b_K"], self.curves["b_U"], self.curves["b_E"]]
            )

    def _setup_ui_controls(self) -> None:
        """Injects UI buttons and drop-down selectors into the VPython DOM."""
        self.btn_pause = button(
            text="⏸ PAUSE", bind=self.toggle_pause, background=color.orange
        )
        self.scene.append_to_caption("  ")
        button(text="🔄 RESTART", bind=self.restart_sim, background=color.blue)

        self.scene.append_to_caption("<b>  Active Reference:</b> &nbsp;&nbsp;")
        self.btn_ground = button(
            text="◉ GROUND",
            bind=lambda b: self.change_ref("ground"),
            background=color.green,
        )
        self.scene.append_to_caption("  ")
        self.btn_cell = button(
            text="○ CELLPHONE",
            bind=lambda b: self.change_ref("cellphone"),
            background=color.gray(0.5),
        )
        self.scene.append_to_caption("  ")
        self.btn_balloon = button(
            text="○ BALLOON",
            bind=lambda b: self.change_ref("balloon"),
            background=color.gray(0.5),
        )

        self.scene.append_to_caption("\n<b>Display Graphs:</b> &nbsp;&nbsp;")
        self.menu_graphs = menu(
            choices=["ALL", "Position", "Cellphone Energy", "Balloon Energy"],
            selected="Position",
            bind=self._on_graph_menu_change,
        )
        self.scene.append_to_caption("\n<hr>")

    # --- Event Handlers ---

    def _on_graph_menu_change(self, m: menu) -> None:
        """Safe handler with type narrowing for the menu widget."""
        selected_option: Optional[str] = m.selected
        if not selected_option:
            return

        mapping: Dict[str, str] = {
            "ALL": "all",
            "Position": "pos",
            "Cellphone Energy": "cell_eng",
            "Balloon Energy": "balloon_eng",
        }

        if selected_option in mapping:
            self.set_graph_view(mapping[selected_option])

    def set_graph_view(self, view_mode: str) -> None:
        """Re-initializes active graph containers and replots history."""
        if self.active_graph_view == view_mode:
            return

        self.active_graph_view = view_mode
        self._setup_graphs()
        self._replot_history()

    def toggle_pause(self, b) -> None:
        self.is_running = not self.is_running
        self.btn_pause.text = "▶ PLAY" if not self.is_running else "⏸ PAUSE"
        self.btn_pause.background = color.green if not self.is_running else color.orange

    def restart_sim(self, b) -> None:
        self.t = 0.0
        for curve in self.all_curves:
            curve.data = []
        
        # Reset visual meshes based on t=0 snapshot
        self._update_visuals(self.engine.get_snapshot(self.t, self.active_ref))
        
        if not self.is_running:
            self.toggle_pause(self.btn_pause)

    def change_ref(self, selected_ref: str) -> None:
        """Changes reference frame and replots historical telemetry."""
        self.active_ref = selected_ref

        self.btn_ground.text = "◉ GROUND" if selected_ref == "ground" else "○ GROUND"
        self.btn_cell.text = (
            "◉ CELLPHONE" if selected_ref == "cellphone" else "○ CELLPHONE"
        )
        self.btn_balloon.text = (
            "◉ BALLOON" if selected_ref == "balloon" else "○ BALLOON"
        )

        self.btn_ground.background = (
            color.green if selected_ref == "ground" else color.gray(0.5)
        )
        self.btn_cell.background = (
            color.green if selected_ref == "cellphone" else color.gray(0.5)
        )
        self.btn_balloon.background = (
            color.green if selected_ref == "balloon" else color.gray(0.5)
        )

        for curve in self.all_curves:
            curve.data = []

        self._replot_history()

    def _replot_history(self) -> None:
        """Re-evaluates engine state from 0 to current t for active curves."""
        history_t = 0.0
        while history_t <= self.t:
            snap = self.engine.get_snapshot(history_t, self.active_ref)
            self._plot_graphs(history_t, snap)
            history_t += self.dt

    # --- Render Loop ---

    def _update_visuals(self, snapshot: dict) -> None:
        """Updates 3D mesh positions."""
        self.meshes["cellphone"].pos.y = snapshot["cellphone"]["abs_y"]
        self.meshes["balloon"].pos.y = snapshot["balloon"]["abs_y"]

    def _plot_graphs(self, current_time: float, snapshot: dict) -> None:
        """Appends points only to instantiated active curves."""
        cell = snapshot["cellphone"]
        balloon = snapshot["balloon"]

        if "c_pos" in self.curves:
            self.curves["c_pos"].plot(current_time, cell["rel_y"])
        if "b_pos" in self.curves:
            self.curves["b_pos"].plot(current_time, balloon["rel_y"])

        if "c_K" in self.curves:
            self.curves["c_K"].plot(current_time, cell["energies"].kinetic)
        if "c_U" in self.curves:
            self.curves["c_U"].plot(current_time, cell["energies"].potential)
        if "c_E" in self.curves:
            self.curves["c_E"].plot(current_time, cell["energies"].mechanical)

        if "b_K" in self.curves:
            self.curves["b_K"].plot(current_time, balloon["energies"].kinetic)
        if "b_U" in self.curves:
            self.curves["b_U"].plot(current_time, balloon["energies"].potential)
        if "b_E" in self.curves:
            self.curves["b_E"].plot(current_time, balloon["energies"].mechanical)

    def run(self) -> None:
        """Main rendering loop."""
        while True:
            rate(60)
            if self.is_running:
                snapshot = self.engine.get_snapshot(self.t, self.active_ref)

                if (
                    snapshot["cellphone"]["abs_y"]
                    > self.meshes["ground"].pos.y
                    + self.meshes["cellphone"].size.y / 2
                ):
                    self._update_visuals(snapshot)
                    self._plot_graphs(self.t, snapshot)
                    self.t += self.dt


if __name__ == "__main__":
    # 1. Instantiate the Domain (Physics)
    cellphone_model = PointMass(name="cellphone", mass=1.0, initial_y=10.0, initial_v=10.0, accel=-GRAVITY)
    balloon_model = PointMass(name="balloon", mass=1.0, initial_y=10.0, initial_v=10.0, accel=0.0)
    
    engine = SimulationEngine(objects={
        "cellphone": cellphone_model,
        "balloon": balloon_model
    })
    
    # 2. Inject Domain into Presentation Layer and run
    app = VPythonRenderer(engine)
    app.run()