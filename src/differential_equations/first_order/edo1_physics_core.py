# physics_core.py
import math
from dataclasses import dataclass
from typing import Dict, Tuple, Callable

GRAVITY = 9.81

@dataclass(frozen=True)
class ODEState:
    """"""
    t: float
    y: Tuple[float, ...]


class DifferentialEquation:
    """
    """
    def __init__(
            self, 
            derivative: Callable[[float, Tuple[float, ...]], Tuple[float, ...]],
            initial_time: float,
            initial_state: Tuple[float, ...]
        ):
        self.derivative = derivative
        self.initial_time = initial_time
        self.initial_state = initial_state

    def evaluate(self, t: float, state: Tuple[float, ...]):
        """Evaluate the derivative f(t, y)."""
        return self.derivative(t, state)
            

class ODESolver:
    def __init__(
        self,
        ode: DifferentialEquation,
        step_size: float,
    ):
        if step_size <= 0:
            raise ValueError("Step size must be positive.")

        self.ode = ode
        self.step_size = step_size

    def step(self, state: ODEState) -> ODEState:
        """
        Perform one numerical integration step.

        Must be implemented by subclasses.
        """

        raise NotImplementedError

    def solve(self, final_time: float) -> list[ODEState]:
        """
        Numerically solve the ODE from the initial condition
        until final_time.
        """

        raise NotImplementedError
    pass

class EulerSolver(ODESolver):
    """Numerical solver based on the explicit Euler method."""

    pass

class RK4Solver(ODESolver):
    """Numerical solver based on the 4th-order Runge-Kutta method."""
    pass


class SimulationEngine:
    """
    Orchestrates the numerical solution of the differential equation.
    """

    def __init__(self, solver: ODESolver):
        self.solver = solver

    def run(self, final_time: float) -> list[ODEState]:
        return self.solver.solve(final_time)