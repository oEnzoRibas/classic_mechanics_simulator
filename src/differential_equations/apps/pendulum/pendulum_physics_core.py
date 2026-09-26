from dataclasses import dataclass
from typing import Tuple

import numpy as np

from differential_equations.edo_physics_core import (
    DifferentialEquation,
    ODEState,
)


@dataclass
class PendulumSimulationResult:

    states: list[ODEState]

    @property
    def times(self) -> list[float]:
        return [
            state.t
            for state in self.states
        ]

    @property
    def positions(self) -> list[float]:
        return [
            state.y[0]
            for state in self.states
        ]

    @property
    def velocities(self) -> list[float]:
        return [
            state.y[1]
            for state in self.states
        ]
    
class PendulumPhysicsCore:

    def __init__(
        self,
        g: float = 9.81,
        L: float = 1.0,
        mu: float = 0.2,
        initial_position: float = np.deg2rad(-145),
        initial_velocity: float = 6.4,
        step_size: float = 0.001,
    ) -> None:

        """
        @param g The gravitational Force
        @param L The Pendulum bar lenght
        @param mu The dumping coefficient
        """

        self.g = g
        self.L = L
        self.mu = mu

        self.initial_position = initial_position
        self.initial_velocity = initial_velocity

    def derivative(
        self,
        t: float,
        state: Tuple[float, ...]
    ) -> Tuple[float, ...]:
        x, velocity = state

        dx_dt = velocity
        dvelocity_dt = (
            -self.g/self.L * np.sin(x) - self.mu * velocity
        )

        return (
            dx_dt,
            dvelocity_dt,
        )
    
    def create_ode(self) -> DifferentialEquation:
        return DifferentialEquation(
            derivative=self.derivative,
            initial_time=0.0,
            initial_state=(
                self.initial_position,
                self.initial_velocity,
            ),
        )
    
    def bob_position(
        self,
        position: float,
    ) -> tuple[float, float]:

        return (
            self.L * np.sin(position),
            -self.L * np.cos(position),
        )
    
    