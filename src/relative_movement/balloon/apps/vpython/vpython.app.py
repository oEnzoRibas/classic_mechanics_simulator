# vpython_app.py
from vpython import *
from relative_movement.balloon.physics_core import PointMass, SimulationEngine, GRAVITY

# --- UI Constants ---
GRAPH_W = 650
GRAPH_H = 200

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
            "ground": box(pos=vec(0, 0, 0), size=vec(30, 0.2, 30), color=color.gray(0.5)),
            "balloon": sphere(pos=vec(-2, 10, 3), radius=1.2, color=color.cyan),
            "cellphone": box(pos=vec(2, 10, 3), size=vec(2, 2, 2), color=color.red)
        }
        
    def _setup_graphs(self) -> None:
        """Builds the graphical plots for relative positions and energies."""
        pos_graph = graph(align="right", title="<b>Relative Position (m)</b>", width=GRAPH_W, height=GRAPH_H, xmax=2.8)
        self.curve_c_pos = gcurve(graph=pos_graph, color=color.red, label="Cellphone")
        self.curve_b_pos = gcurve(graph=pos_graph, color=color.cyan, label="Balloon")

        c_eng_graph = graph(align="right", title="<b>Cellphone Energy (J)</b>", width=GRAPH_W, height=GRAPH_H, xmax=2.8)
        self.curve_c_K = gcurve(graph=c_eng_graph, color=color.blue, label="Kinetic (K)")
        self.curve_c_U = gcurve(graph=c_eng_graph, color=color.orange, label="Potential (U)")
        self.curve_c_E = gcurve(graph=c_eng_graph, color=color.red, label="Mechanical (E)")

        b_eng_graph = graph(align="right", title="<b>Balloon Energy (J)</b>", width=GRAPH_W, height=GRAPH_H, xmax=2.8)
        self.curve_b_K = gcurve(graph=b_eng_graph, color=color.blue, label="Kinetic (K)")
        self.curve_b_U = gcurve(graph=b_eng_graph, color=color.orange, label="Potential (U)")
        self.curve_b_E = gcurve(graph=b_eng_graph, color=color.cyan, label="Mechanical (E)")
        
        # Store curves for easy clearing
        self.all_curves = [
            self.curve_c_pos, self.curve_b_pos, 
            self.curve_c_K, self.curve_c_U, self.curve_c_E,
            self.curve_b_K, self.curve_b_U, self.curve_b_E
        ]

    def _setup_ui_controls(self) -> None:
        """Injects UI buttons into the VPython DOM and binds event handlers."""
        self.btn_pause = button(text="⏸ PAUSE", bind=self.toggle_pause, background=color.orange)
        self.scene.append_to_caption("  ")
        button(text="🔄 RESTART", bind=self.restart_sim, background=color.blue)

        self.scene.append_to_caption("<b>  Active Reference:</b> &nbsp;&nbsp;")
        self.btn_ground = button(text="◉ GROUND", bind=lambda b: self.change_ref("ground"), background=color.green)
        self.scene.append_to_caption("  ")
        self.btn_cell = button(text="○ CELLPHONE", bind=lambda b: self.change_ref("cellphone"), background=color.gray(0.5))
        self.scene.append_to_caption("  ")
        self.btn_balloon = button(text="○ BALLOON", bind=lambda b: self.change_ref("balloon"), background=color.gray(0.5))
        self.scene.append_to_caption("\n<hr>")

    # --- Event Handlers ---
    
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
        """
        Changes the reference frame and recomputes the historical graph data 
        up to the current time 't'.
        """
        self.active_ref = selected_ref
        
        self.btn_ground.text = "◉ GROUND" if selected_ref == "ground" else "○ GROUND"
        self.btn_cell.text = "◉ CELLPHONE" if selected_ref == "cellphone" else "○ CELLPHONE"
        self.btn_balloon.text = "◉ BALLOON" if selected_ref == "balloon" else "○ BALLOON"
        
        self.btn_ground.background = color.green if selected_ref == "ground" else color.gray(0.5)
        self.btn_cell.background = color.green if selected_ref == "cellphone" else color.gray(0.5)
        self.btn_balloon.background = color.green if selected_ref == "balloon" else color.gray(0.5)
        
        # Re-plot all history for the new reference frame
        for curve in self.all_curves:
            curve.data = []
            
        history_t = 0.0
        while history_t <= self.t:
            snap = self.engine.get_snapshot(history_t, selected_ref)
            self._plot_graphs(history_t, snap)
            history_t += self.dt

    # --- Render Loop ---

    def _update_visuals(self, snapshot: dict) -> None:
        """Updates the 3D meshes based on the domain absolute position."""
        self.meshes["cellphone"].pos.y = snapshot["cellphone"]["abs_y"]
        self.meshes["balloon"].pos.y = snapshot["balloon"]["abs_y"]

    def _plot_graphs(self, current_time: float, snapshot: dict) -> None:
        """Appends new data points to the graphs based on relative snapshot data."""
        cell = snapshot["cellphone"]
        balloon = snapshot["balloon"]
        
        self.curve_c_pos.plot(current_time, cell["rel_y"])
        self.curve_b_pos.plot(current_time, balloon["rel_y"])
        
        self.curve_c_K.plot(current_time, cell["energies"].kinetic)
        self.curve_c_U.plot(current_time, cell["energies"].potential)
        self.curve_c_E.plot(current_time, cell["energies"].mechanical)
        
        self.curve_b_K.plot(current_time, balloon["energies"].kinetic)
        self.curve_b_U.plot(current_time, balloon["energies"].potential)
        self.curve_b_E.plot(current_time, balloon["energies"].mechanical)

    def run(self) -> None:
        """Main rendering loop."""
        while True:
            rate(60)
            if self.is_running:
                snapshot = self.engine.get_snapshot(self.t, self.active_ref)
                
                # Stop condition (if cellphone hits ground)
                if snapshot["cellphone"]["abs_y"] > self.meshes["ground"].pos.y + self.meshes["cellphone"].size.y / 2:
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