"""Compatibility import for the previous balloon-specific physics-core path.

New code should import from ``relative_movement.physics_core`` directly.
This module contains no physics logic and may be removed after all imports
have been migrated.
"""

from relative_movement.physics_core import (
    GRAVITY,
    GROUND_REFERENCE,
    EnergyState,
    KinematicState,
    PointMass,
    SimulationEngine,
)

__all__ = [
    "GRAVITY",
    "GROUND_REFERENCE",
    "KinematicState",
    "EnergyState",
    "PointMass",
    "SimulationEngine",
]
