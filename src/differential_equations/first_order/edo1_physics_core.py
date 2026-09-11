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
    """
    Base class for numerical ODE solvers.
    """

    def __init__(
        self,
        ode: DifferentialEquation,
        step_size: float,
    ):
        if step_size <= 0:
            raise ValueError("Step size must be positive.")

        self.ode = ode
        self.step_size = step_size

    def step(self, state: ODEState, step_size : float) -> ODEState:
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

        if final_time < self.ode.initial_time:
            raise ValueError(
                "Final time must be greater than or equal "
                "to the initial time."
            )

        state = ODEState(
            t=self.ode.initial_time,
            y=self.ode.initial_state,
        )

        states = [state]

        while state.t < final_time:
            remaining_time = final_time - state.t

            # Avoid overshooting the requested final time.
            step_size = min(self.step_size, remaining_time)

            state = self.step(state, step_size)
            states.append(state)

        return states

class EulerSolver(ODESolver):
    """Numerical solver based on the explicit Euler method."""

    pass

class RK4Solver(ODESolver):
    """Numerical solver based on the classical fourth-order Runge-Kutta method."""

    def step(
        self,
        state: ODEState,
        step_size: float,
    ) -> ODEState:

        t = state.t
        y = state.y

        k1 = self.ode.evaluate(t, y)

        y_k2 = tuple(
            yi + (step_size / 2.0) * k1i
            for yi, k1i in zip(y, k1)
        )

        k2 = self.ode.evaluate(
            t + step_size / 2.0,
            y_k2,
        )

        y_k3 = tuple(
            yi + (step_size / 2.0) * k2i
            for yi, k2i in zip(y, k2)
        )

        k3 = self.ode.evaluate(
            t + step_size / 2.0,
            y_k3,
        )

        y_k4 = tuple(
            yi + step_size * k3i
            for yi, k3i in zip(y, k3)
        )

        k4 = self.ode.evaluate(
            t + step_size,
            y_k4,
        )

        next_y = tuple(
            yi + (step_size / 6.0)
            * (k1i + 2.0 * k2i + 2.0 * k3i + k4i)
            for yi, k1i, k2i, k3i, k4i
            in zip(y, k1, k2, k3, k4)
        )

        return ODEState(
            t=t + step_size,
            y=next_y,
        )


class SimulationEngine:
    """
    Orchestrates the numerical solution of the differential equation.
    """

    def __init__(self, solver: ODESolver):
        self.solver = solver

    def run(self, final_time: float) -> list[ODEState]:
        return self.solver.solve(final_time)