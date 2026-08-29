"""
Manim Presentation Layer (Adapter).
Generates deterministic, high-quality videos for each reference frame.
Features dynamic path resolution, clean code separation, and adaptive graph limits.
"""

import sys
import math
from pathlib import Path
from manim import *

# ==========================================
# 1. ROBUST PATH RESOLUTION & MANIM CONFIG
# ==========================================
current_file = Path(__file__).resolve()
src_path = current_file.parent

while src_path.name != "src" and src_path.parent != src_path:
    src_path = src_path.parent

if src_path.name == "src":
    sys.path.append(str(src_path))
else:
    raise RuntimeError("Could not find 'src' directory. Ensure this script is inside 'src'.")

config.media_dir = str(current_file.parent / "output")

from relative_movement.balloon.physics_core import PointMass, SimulationEngine, GRAVITY

CYAN = "#00FFFF"
RED = "#F00000"


class BaseBalloonScene(Scene):
    """
    Base class orchestrating the physical domain mesh generation and the stacked-graph layout.
    
    Attributes:
        active_reference (str): The name of the reference frame to compute relative physics against.
        auto_adapt_limits (bool): Set to True to pre-calculate max/min bounds, False to use static ranges.
        pos_y_range (list): Static boundary format [min_y, max_y, tick_step] for position axes.
        c_eng_y_range (list): Static boundary format [min_y, max_y, tick_step] for cellphone energy axes.
        b_eng_y_range (list): Static boundary format [min_y, max_y, tick_step] for balloon energy axes.
    """
    active_reference = "ground"
    
    auto_adapt_limits = False 
    
    pos_y_range = [-50, 30, 20]
    c_eng_y_range = [-500, 500, 250]
    b_eng_y_range = [-500, 500, 250]

    def construct(self):
        """
        Builds the visual hierarchy and executes the animation timeline deterministically.

        Returns:
            None
        """
        cellphone_model = PointMass(name="cellphone", mass=1.0, initial_y=10.0, initial_v=10.0, accel=-GRAVITY)
        balloon_model = PointMass(name="balloon", mass=1.0, initial_y=10.0, initial_v=10.0, accel=0.0)
        
        self.engine = SimulationEngine(objects={
            "cellphone": cellphone_model,
            "balloon": balloon_model
        })
        
        self.time_tracker = ValueTracker(0.0)
        self.physics_scale = 0.2
        self.ground_y = -3.0

        if self.auto_adapt_limits:
            self._calculate_dynamic_ranges()

        self._build_physical_meshes()
        self._build_graphs()
        self._bind_updaters()

        self.wait(0.5)
        self.play(
            self.time_tracker.animate.set_value(2.8),
            run_time=5,
            rate_func=linear
        )
        self.wait(1)

    def _calculate_dynamic_ranges(self):
        """
        Simulates the entire time window upfront to find absolute maximums and minimums,
        adapting the Y axes boundaries to perfectly fit the generated data.

        Returns:
            None

        Notes:
            - Rounds bounds to nearest 10s for cleaner axes numbers.
        """
        t, t_max, dt = 0.0, 3.0, 0.1
        pos_vals, c_eng_vals, b_eng_vals = [], [], []
        
        while t <= t_max:
            snap = self.engine.get_snapshot(t, self.active_reference)
            pos_vals.extend([snap["cellphone"]["rel_y"], snap["balloon"]["rel_y"]])
            
            c_e = snap["cellphone"]["energies"]
            c_eng_vals.extend([c_e.kinetic, c_e.potential, c_e.mechanical])
            
            b_e = snap["balloon"]["energies"]
            b_eng_vals.extend([b_e.kinetic, b_e.potential, b_e.mechanical])
            
            t += dt
            
        def get_padded_range(vals, steps=4):
            """
            Computes padded axis boundaries and step sizes based on raw data limits.

            Args:
                vals (list): List of numerical data points.
                steps (int, optional): The target number of tick steps on the axis. Defaults to 4.

            Returns:
                list: A list containing [min_bound, max_bound, tick_step].
            """
            min_v, max_v = min(vals), max(vals)
            padding = (max_v - min_v) * 0.1 if min_v != max_v else 10.0
            
            min_b = math.floor((min_v - padding) / 10) * 10
            max_b = math.ceil((max_v + padding) / 10) * 10
            step_b = max(1, int((max_b - min_b) / steps))
            
            return [min_b, max_b, step_b]

        self.pos_y_range = get_padded_range(pos_vals)
        self.c_eng_y_range = get_padded_range(c_eng_vals)
        self.b_eng_y_range = get_padded_range(b_eng_vals)

    def _build_physical_meshes(self):
        """
        Instantiates the 3D domain representations on the left side.

        Returns:
            None
        """
        self.ground_line = Line(start=LEFT*7, end=LEFT*1, color=GRAY, stroke_width=4).shift(UP * self.ground_y)
        self.cell_mesh = Square(side_length=0.4, color=RED, fill_opacity=0.8)
        self.balloon_mesh = Circle(radius=0.4, color=TEAL, fill_opacity=0.8)
        
        scene_title = Text(f"Ref: {self.active_reference.capitalize()}", font_size=32, color=YELLOW).to_corner(UL)
        self.add(self.ground_line, self.cell_mesh, self.balloon_mesh, scene_title)

    def _build_graphs(self):
        """
        Constructs the vertically stacked triple graph layout on the right side.

        Returns:
            None
        """
        axes_config = {
            "x_range": [0, 3, 1], 
            "x_length": 6.0,      
            "y_length": 1.7,      
            "axis_config": {"include_numbers": True, "font_size": 14}
        }

        self.pos_axes = Axes(y_range=self.pos_y_range, **axes_config)
        self.c_eng_axes = Axes(y_range=self.c_eng_y_range, **axes_config)
        self.b_eng_axes = Axes(y_range=self.b_eng_y_range, **axes_config)

        pos_group = VGroup(Text("Relative Y (m)", font_size=16), self.pos_axes).arrange(DOWN, buff=0.1)
        c_eng_group = VGroup(Text("Cell Energy (J)", font_size=16), self.c_eng_axes).arrange(DOWN, buff=0.1)
        b_eng_group = VGroup(Text("Balloon Energy (J)", font_size=16), self.b_eng_axes).arrange(DOWN, buff=0.1)

        graphs_group = VGroup(pos_group, c_eng_group, b_eng_group).arrange(DOWN, buff=0.3).to_edge(RIGHT, buff=0.5)
        self.add(graphs_group)

    def _bind_updaters(self):
        """
        Binds the continuous ValueTracker updates to the meshes and traces using clean factory methods.

        Returns:
            None
        """
        self.cell_mesh.add_updater(
            lambda m: m.move_to(
                LEFT * 4.5 + UP * ((self.engine.get_snapshot(self.time_tracker.get_value(), "ground")["cellphone"]["abs_y"] * self.physics_scale) + self.ground_y)
            )
        )
        
        self.balloon_mesh.add_updater(
            lambda m: m.move_to(
                LEFT * 2.5 + UP * ((self.engine.get_snapshot(self.time_tracker.get_value(), "ground")["balloon"]["abs_y"] * self.physics_scale) + self.ground_y)
            )
        )

        cell_pos_dot = self._create_pos_dot("cellphone", RED)
        balloon_pos_dot = self._create_pos_dot("balloon", CYAN)
        
        self.add(
            cell_pos_dot, balloon_pos_dot, 
            TracedPath(cell_pos_dot.get_center, stroke_color=RED, stroke_width=3), 
            TracedPath(balloon_pos_dot.get_center, stroke_color=CYAN, stroke_width=3)
        )

        self._inject_energy_traces("cellphone", self.c_eng_axes)

        self._inject_energy_traces("balloon", self.b_eng_axes)

    def _create_pos_dot(self, entity_name: str, dot_color: "ManimColor | str"):
        """
        Creates a dynamic dot mapped to an entity's relative position.

        Args:
            entity_name (str): The identifier of the physical entity (e.g., 'cellphone' or 'balloon').
            dot_color (ManimColor | str): The color for the dot (accepts ManimColor constants or HEX strings).

        Returns:
            Mobject: A Manim Mobject (Dot) wrapped in an always_redraw updater.
        """
        return always_redraw(
            lambda: Dot(
                self.pos_axes.c2p(
                    self.time_tracker.get_value(), 
                    self.engine.get_snapshot(self.time_tracker.get_value(), self.active_reference)[entity_name]["rel_y"]
                ),
                color=dot_color, 
                radius=0.06
            )
        )

    def _inject_energy_traces(self, entity_name: str, target_axes: Axes):
        """
        Generates and adds the Kinetic, Potential, and Mechanical energy traces to a given axis.

        Args:
            entity_name (str): The identifier of the physical entity whose energies will be plotted.
            target_axes (Axes): The Manim Axes instance where the energy dots and traces will be drawn.

        Returns:
            None
        """
        k_dot = always_redraw(
            lambda: 
            Dot(
                target_axes.c2p(
                    self.time_tracker.get_value(), 
                    getattr(
                        self.engine.get_snapshot(
                            self.time_tracker.get_value(), 
                            self.active_reference
                            )[entity_name]["energies"], "kinetic")), 
                            color=BLUE, 
                            radius=0.06
                )
        )
        u_dot = always_redraw(
            lambda: 
            Dot(
                target_axes.c2p(
                    self.time_tracker.get_value(), 
                    getattr(
                        self.engine.get_snapshot(
                            self.time_tracker.get_value(), 
                            self.active_reference
                            )[entity_name]["energies"], 
                            "potential"
                            )
                    ), 
                    color=ORANGE, 
                    radius=0.06
                )
        )
        e_dot = always_redraw(
            lambda: 
            Dot(
                target_axes.c2p(
                    self.time_tracker.get_value(), 
                    getattr(
                        self.engine.get_snapshot(
                            self.time_tracker.get_value(), 
                            self.active_reference
                            )[entity_name]["energies"], 
                            "mechanical"
                            )
                ), 
                color=RED, 
                radius=0.06
                )
        )
        
        self.add(
            k_dot, u_dot, e_dot, 
            TracedPath(k_dot.get_center, stroke_color=BLUE, stroke_width=3), 
            TracedPath(u_dot.get_center, stroke_color=ORANGE, stroke_width=3), 
            TracedPath(e_dot.get_center, stroke_color=RED, stroke_width=3)
        )

class GroundScene(BaseBalloonScene):
    """
    Generates the MP4 for the Ground reference frame.

    Notes:
        - Utilizes custom static limits for the Ground reference frame.
    """
    active_reference = "ground"
    auto_adapt_limits = True
    
    # pos_y_range = [-5, 35, 10]
    # c_eng_y_range = [-100, 200, 100]
    # b_eng_y_range = [-100, 200, 100]

class CellphoneScene(BaseBalloonScene):
    """
    Generates the MP4 for the Cellphone reference frame.

    Notes:
        - Because auto_adapt_limits is True, it will ignore any static boundaries provided here.
    """
    active_reference = "cellphone"
    auto_adapt_limits = True 
    # pos_y_range = [-30, 10, 10]
    # c_eng_y_range = [-400, 200, 200]
    # b_eng_y_range = [0, 10, 5]

class BalloonScene(BaseBalloonScene):
    """
    Generates the MP4 for the Balloon reference frame.

    Notes:
        - Utilizes custom static limits for the Balloon reference frame.
    """
    active_reference = "balloon"
    auto_adapt_limits = True
    
    # pos_y_range = [-30, 10, 10]
    # c_eng_y_range = [-400, 200, 200]
    # b_eng_y_range = [0, 10, 5]