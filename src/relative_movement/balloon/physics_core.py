# physics_core.py
import math
from dataclasses import dataclass
from typing import Dict, Tuple

GRAVITY = 9.81

@dataclass(frozen=True)
class KinematicState:
    """Data Transfer Object (DTO) representing the kinematic state at a given time."""
    y: float
    v: float

@dataclass(frozen=True)
class EnergyState:
    """Data Transfer Object (DTO) representing the energetic state of a mass."""
    kinetic: float
    potential: float
    mechanical: float

class PointMass:
    """
    Domain model encapsulating the intrinsic properties of a point mass.
    Calculates its state deterministically as a pure function of time.
    """
    def __init__(self, name: str, mass: float, initial_y: float, initial_v: float, accel: float):
        self.name = name
        self.mass = mass
        self.initial_y = initial_y
        self.initial_v = initial_v
        self.accel = accel

    def get_state_at(self, t: float) -> KinematicState:
        """
        Calculates the exact kinematic state at an arbitrary time 't'.
        Uses closed-form kinematic equations to prevent numerical integration drift.
        """
        y = self.initial_y + (self.initial_v * t) + (0.5 * self.accel * (t ** 2))
        v = self.initial_v + (self.accel * t)
        return KinematicState(y=y, v=v)

    def get_energy_at(self, state: KinematicState, ref_y: float, ref_v: float, gravity: float = GRAVITY) -> EnergyState:
        """
        Calculates the kinetic, potential, and mechanical energies relative to a moving frame.
        """
        y_rel = state.y - ref_y
        v_rel = state.v - ref_v
        
        k = 0.5 * self.mass * (v_rel ** 2)
        u = self.mass * gravity * y_rel
        return EnergyState(kinetic=k, potential=u, mechanical=k + u)


class SimulationEngine:
    """
    Core orchestrator that resolves relative frames and computes the global simulation snapshot.
    """
    def __init__(self, objects: Dict[str, PointMass]):
        self.objects = objects
        
    def get_snapshot(self, t: float, active_ref: str = "ground") -> dict:
        """
        Generates a complete snapshot of the system at time 't'.
        
        Args:
            t (float): The current time in the simulation.
            active_ref (str): The name of the reference frame ("ground" or a PointMass name).
            
        Returns:
            dict: A payload containing absolute positions, relative positions, and energies.
        """
        # 1. Compute absolute states (ground reference)
        abs_states = {name: obj.get_state_at(t) for name, obj in self.objects.items()}
        
        # 2. Determine the origin of the active reference frame
        if active_ref == "ground":
            ref_y, ref_v = 0.0, 0.0
        else:
            ref_state = abs_states[active_ref]
            ref_y, ref_v = ref_state.y, ref_state.v
            
        # 3. Build the payload snapshot
        snapshot = {}
        for name, obj in self.objects.items():
            state = abs_states[name]
            y_rel = state.y - ref_y
            v_rel = state.v - ref_v
            energies = obj.get_energy_at(state, ref_y, ref_v)
            
            snapshot[name] = {
                "abs_y": state.y,
                "abs_v": state.v,
                "rel_y": y_rel,
                "rel_v": v_rel,
                "energies": energies
            }
            
        return snapshot