"""Generic one-dimensional relative-motion physics, independent of renderers.

Coordinates: y increases upward. Positive velocity/acceleration point upward.

The model uses constant acceleration for each body. The reserved ``ground``
reference is fixed at y=0, v=0, a=0. Other references follow a simulated body.

Relative kinetic energy and gravitational potential energy are *instantaneous*
quantities in the selected reference. Their sum need not be conserved in a
moving or accelerated reference frame (or for externally driven objects).
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping

GRAVITY = 9.81
GROUND_REFERENCE = "ground"


@dataclass(frozen=True)
class KinematicState:
    """Absolute position and velocity of a body at a given time (SI units)."""

    y: float
    v: float


@dataclass(frozen=True)
class EnergyState:
    """Relative kinetic, gravitational potential, and total energy (joules)."""

    kinetic: float
    potential: float
    mechanical: float


class PointMass:
    """Point mass moving along the vertical axis with constant acceleration."""

    def __init__(
        self,
        name: str,
        mass: float,
        initial_y: float,
        initial_v: float,
        accel: float,
    ) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Object name must be a nonempty string.")
        for field_name, value in (
            ("mass", mass),
            ("initial_y", initial_y),
            ("initial_v", initial_v),
            ("accel", accel),
        ):
            if not isfinite(value):
                raise ValueError(f"{field_name} must be finite.")
        if mass <= 0:
            raise ValueError("Mass must be positive.")

        self.name = name
        self.mass = mass
        self.initial_y = initial_y
        self.initial_v = initial_v
        self.accel = accel

    def get_state_at(self, t: float) -> KinematicState:
        """Return absolute y(t) and v(t); negative times are allowed."""
        if not isfinite(t):
            raise ValueError("Time must be finite.")
        return KinematicState(
            y=self.initial_y + self.initial_v * t + 0.5 * self.accel * t**2,
            v=self.initial_v + self.accel * t,
        )

    def get_energy_at(
        self,
        state: KinematicState,
        ref_y: float,
        ref_v: float,
        gravity: float = GRAVITY,
    ) -> EnergyState:
        """Calculate relative K and gravitational U (zero at reference y).

        This quantity does not include fictitious-force potentials. In an
        accelerated reference frame, ``mechanical`` is not generally conserved.
        """
        if not isfinite(gravity) or gravity < 0:
            raise ValueError("Gravity must be finite and nonnegative.")
        y_rel = state.y - ref_y
        v_rel = state.v - ref_v
        kinetic = 0.5 * self.mass * v_rel**2
        potential = self.mass * gravity * y_rel
        return EnergyState(kinetic, potential, kinetic + potential)


class SimulationEngine:
    """Compute absolute/relative kinematics and energies for any named bodies.

    Reference frames are ``ground`` or the name of any body in ``objects``.
    No assumptions are made about object names, count, or acceleration.
    """

    def __init__(
        self,
        objects: Mapping[str, PointMass],
        gravity: float = GRAVITY,
    ) -> None:
        if not isfinite(gravity) or gravity < 0:
            raise ValueError("Gravity must be finite and nonnegative.")
        if GROUND_REFERENCE in objects:
            raise ValueError('The name "ground" is reserved for the fixed frame.')
        if any(not isinstance(name, str) or not name.strip() for name in objects):
            raise ValueError("Object names must be nonempty strings.")
        if any(not isinstance(obj, PointMass) for obj in objects.values()):
            raise TypeError("All simulated objects must be PointMass instances.")

        self.objects: dict[str, PointMass] = dict(objects)
        self.gravity = gravity

    @property
    def reference_frames(self) -> tuple[str, ...]:
        """Available reference frame names."""
        return (GROUND_REFERENCE, *self.objects.keys())

    def get_snapshot(
        self,
        t: float,
        active_ref: str = GROUND_REFERENCE,
    ) -> dict[str, dict]:
        """Compute the states of all bodies at time ``t``.

        Existing keys ``abs_y``, ``abs_v``, ``rel_y``, ``rel_v`` and ``energies``
        are preserved. ``abs_a`` and ``rel_a`` are added for generic use.
        """
        if not isfinite(t):
            raise ValueError("Time must be finite.")

        absolute = {
            name: obj.get_state_at(t)
            for name, obj in self.objects.items()
        }
        if active_ref == GROUND_REFERENCE:
            ref_y = ref_v = ref_a = 0.0
        else:
            if active_ref not in absolute:
                raise ValueError(f"Unknown reference frame: {active_ref}")
            ref_state = absolute[active_ref]
            ref_y, ref_v = ref_state.y, ref_state.v
            ref_a = self.objects[active_ref].accel

        snapshot: dict[str, dict] = {}
        for name, obj in self.objects.items():
            state = absolute[name]
            snapshot[name] = {
                "abs_y": state.y,
                "abs_v": state.v,
                "abs_a": obj.accel,
                "rel_y": state.y - ref_y,
                "rel_v": state.v - ref_v,
                "rel_a": obj.accel - ref_a,
                "energies": obj.get_energy_at(
                    state, ref_y, ref_v, gravity=self.gravity
                ),
            }
        return snapshot
