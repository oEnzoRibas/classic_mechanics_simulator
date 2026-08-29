from vpython import *
from typing import Dict, List, Tuple

GRAVITY = 9.81

scene = canvas(
    align="left",
    width=520, height=600,
    background=vector(0.15, 0.15, 0.15),
    title="<h2>Cinemática e Referenciais</h2>"
)
scene.center = vec(0, 20, 30)
scene.range = 10
GRAPH_W = 650
GRAPH_H = 200

class PonctualMass:
    """
    Represents a physical point mass. 
    Encapsulates its physical properties, kinematic state, and 3D mesh representation.
    """
    def __init__(self, name: str, mass: float, initial_y: float, initial_v: float, accel: float, mesh):
        """
        Initializes the point mass.

        Args:
            name (str): The identifier for the mass.
            mass (float): The mass value in kilograms.
            initial_y (float): The initial vertical position in meters.
            initial_v (float): The initial vertical velocity in m/s.
            accel (float): The constant vertical acceleration in m/s^2.
            mesh (vpython.3dobject): The VPython 3D object bound to this mass.
        """
        self.name = name
        self.mass = mass
        self.initial_y = initial_y
        self.initial_v = initial_v
        self.accel = accel
        self.mesh = mesh
        
        self.y = initial_y
        self.v = initial_v

    def reset_state(self) -> None:
        """Restores the point mass to its initial kinematic state and resets its 3D mesh position."""
        self.y = self.initial_y
        self.v = self.initial_v
        self.mesh.pos.y = self.initial_y

    def update_kinematics(self, t: float) -> None:
        """Updates the vertical position and velocity at a given time 't' using exact kinematic equations."""
        self.y = self.initial_y + (self.initial_v * t) + (0.5 * self.accel * (t ** 2))
        self.v = self.initial_v + (self.accel * t)
        self.mesh.pos.y = self.y

    def compute_relative_energies(self, gravity: float, ref_y: float, ref_v: float) -> Tuple[float, float, float]:
        """Calculates kinetic, potential, and mechanical energies relative to an arbitrary reference frame."""
        y_rel = self.y - ref_y
        v_rel = self.v - ref_v
        
        k = 0.5 * self.mass * (v_rel ** 2)
        u = self.mass * gravity * y_rel
        return k, u, k + u


class SimulationApp:
    """
    Manages the simulation lifecycle, the user interface, and data orchestration.
    """
    def __init__(self, obj_cell: PonctualMass, obj_balloon: PonctualMass):
        """
        Initializes the simulation application with the given point masses.
        """
        self.cell = obj_cell
        self.balloon = obj_balloon
        
        self.dt = 0.01
        self.t = 0.0
        self.is_running = True
        self.active_ref = "ground"
        
        self.refs = ["ground", "cellphone", "balloon"]
        self.vars_keys = ["t", "c_y", "b_y", "c_K", "c_U", "c_E", "b_K", "b_U", "b_E"]
        self.history = {r: {k: [] for k in self.vars_keys} for r in self.refs}
        
        self.setup_graphs()
        self.setup_ui()

    def setup_graphs(self) -> None:
        """Builds the graphical plots using a Single-View Data-Driven pattern."""
        pos_graph = graph(
            align="right", 
            title="<b>Posição Relativa (m)</b>", 
            width=GRAPH_W, 
            height=GRAPH_H, 
            # xmin=0, 
            xmax=2.8, 
            # ymin=-25, 
            # ymax=25,
        )
        self.c_pos = gcurve(graph=pos_graph, color=color.red, label="Celular")
        self.b_pos = gcurve(graph=pos_graph, color=color.cyan, label="Balão")

        c_eng_graph = graph(
            align="right", 
            title="<b>Energia Celular (J)</b>", 
            width=GRAPH_W, 
            height=GRAPH_H, 
            # xmin=0, 
            xmax=2.8,  
            # ymin=-150, 
            # ymax=350
        )
        self.c_K = gcurve(graph=c_eng_graph, color=color.blue, label="K (Cinética)")
        self.c_U = gcurve(graph=c_eng_graph, color=color.orange, label="U (Potencial)")
        self.c_E = gcurve(graph=c_eng_graph, color=color.red, label="E (Mecânica)")

        b_eng_graph = graph(
            align="right", 
            title="<b>Energia Balão (J)</b>", 
            width=GRAPH_W, 
            height=GRAPH_H, 
            # xmin=0, 
            xmax=2.8, 
            # ymin=-150, 
            # ymax=350
        )
        self.b_K = gcurve(graph=b_eng_graph, color=color.blue, label="K (Cinética)")
        self.b_U = gcurve(graph=b_eng_graph, color=color.orange, label="U (Potencial)")
        self.b_E = gcurve(graph=b_eng_graph, color=color.cyan, label="E (Mecânica)")
        
        self.curves = {
            "c_y": self.c_pos, "b_y": self.b_pos,
            "c_K": self.c_K, "c_U": self.c_U, "c_E": self.c_E,
            "b_K": self.b_K, "b_U": self.b_U, "b_E": self.b_E
        }

    def setup_ui(self) -> None:
        """Injects the control interface into the VPython DOM and maps event handlers."""
        
        self.btn_pause = button(text="⏸ PAUSE", bind=self.toggle_pause, background=color.orange)
        scene.append_to_caption("  ")
        button(text="🔄 RESTART", bind=self.restart_sim, background=color.blue)

        scene.append_to_caption("<b>Referencial Ativo:</b> &nbsp;&nbsp;")
        self.btn_ground = button(text="◉ SOLO", bind=lambda b: self.change_ref("ground"), background=color.green)
        scene.append_to_caption("  ")
        self.btn_cell = button(text="○ CELULAR", bind=lambda b: self.change_ref("cellphone"), background=color.gray(0.5))
        scene.append_to_caption("  ")
        self.btn_balloon = button(text="○ BALÃO", bind=lambda b: self.change_ref("balloon"), background=color.gray(0.5))
        scene.append_to_caption("\n<hr>")

    def toggle_pause(self, b) -> None:
        """Toggles the running state of the simulation and updates the pause button UI."""
        self.is_running = not self.is_running
        self.btn_pause.text = "▶ PLAY" if not self.is_running else "⏸ PAUSE"
        self.btn_pause.background = color.green if not self.is_running else color.orange

    def restart_sim(self, b) -> None:
        """Resets the simulation time, clears all history buffers, and restores objects to their initial states."""
        self.t = 0.0
        self.cell.reset_state()
        self.balloon.reset_state()
        
        for r in self.refs:
            for k in self.vars_keys:
                self.history[r][k].clear()
                
        for curve in self.curves.values():
            curve.data = []
            
        if not self.is_running: 
            self.toggle_pause(self.btn_pause)

    def change_ref(self, selected_ref: str) -> None:
        """Switches the active reference frame, updates UI highlights, and swaps graph data in real-time."""
        self.active_ref = selected_ref
        
        self.btn_ground.text = "◉ SOLO" if selected_ref == "ground" else "○ SOLO"
        self.btn_cell.text = "◉ CELULAR" if selected_ref == "cellphone" else "○ CELULAR"
        self.btn_balloon.text = "◉ BALÃO" if selected_ref == "balloon" else "○ BALÃO"
        
        self.btn_ground.background = color.green if selected_ref == "ground" else color.gray(0.5)
        self.btn_cell.background = color.green if selected_ref == "cellphone" else color.gray(0.5)
        self.btn_balloon.background = color.green if selected_ref == "balloon" else color.gray(0.5)
        
        ref_hist = self.history[selected_ref]
        for key, curve in self.curves.items():
            curve.data = list(zip(ref_hist["t"], ref_hist[key]))

    def _extract_frame_origin(self, ref_name: str) -> Tuple[float, float]:
        """Returns the absolute position and velocity of the specified reference frame origin."""
        if ref_name == "ground": return 0.0, 0.0
        if ref_name == "cellphone": return self.cell.y, self.cell.v
        return self.balloon.y, self.balloon.v

    def step(self) -> None:
        """Executes a single mathematical frame of the simulation, computing kinematics and energies for all frames."""
        self.cell.update_kinematics(self.t)
        self.balloon.update_kinematics(self.t)

        for ref_name in self.refs:
            ref_y, ref_v = self._extract_frame_origin(ref_name)
            
            cy_rel, cv_rel = (self.cell.y - ref_y), (self.cell.v - ref_v)
            by_rel, bv_rel = (self.balloon.y - ref_y), (self.balloon.v - ref_v)

            cK, cU, cE = self.cell.compute_relative_energies(GRAVITY, ref_y, ref_v)
            bK, bU, bE = self.balloon.compute_relative_energies(GRAVITY, ref_y, ref_v)

            rh = self.history[ref_name]
            rh["t"].append(self.t)
            rh["c_y"].append(cy_rel); rh["b_y"].append(by_rel)
            rh["c_K"].append(cK); rh["c_U"].append(cU); rh["c_E"].append(cE)
            rh["b_K"].append(bK); rh["b_U"].append(bU); rh["b_E"].append(bE)

            if ref_name == self.active_ref:
                self.curves["c_y"].plot(self.t, cy_rel); self.curves["b_y"].plot(self.t, by_rel)
                self.curves["c_K"].plot(self.t, cK); self.curves["c_U"].plot(self.t, cU); self.curves["c_E"].plot(self.t, cE)
                self.curves["b_K"].plot(self.t, bK); self.curves["b_U"].plot(self.t, bU); self.curves["b_E"].plot(self.t, bE)

        self.t += self.dt

    def run(self) -> None:
        """Starts the infinite physics execution loop (blocks the main thread)."""
        while True:
            rate(60)

            if self.is_running and self.cell.y > ground3d._pos._y + celular3d.size.y/2:
                self.step()

if __name__ == "__main__":
    ground3d = box(pos=vec(0, 0, 0), size=vec(30, 0.2, 30), color=color.gray(0.5))
    
    balloon3d = sphere(pos=vec(-2, 10, 3), radius=1.2, color=color.cyan)
    celular3d = box(pos=vec(2, 10, 3), size=vec(2, 2, 2), color=color.red)


    initial_velocity = 10.0
    celular = PonctualMass(
        name="Celular", 
        mass=1.0, 
        initial_y=10.0, 
        initial_v=initial_velocity, 
        accel=-GRAVITY, 
        mesh=celular3d
    )
    balloon = PonctualMass(
        name="Balão", 
        mass=1.0, 
        initial_y=10.0, 
        initial_v=initial_velocity, 
        accel=0.0, 
        mesh=balloon3d
    )

    app = SimulationApp(celular, balloon)
    app.run()