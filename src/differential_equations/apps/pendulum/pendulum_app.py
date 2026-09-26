import numpy as np

from differential_equations.edo_physics_core import (
    EulerSolver,
    SimulationEngine,
)

from differential_equations.apps.pendulum.pendulum_physics_core import (
    PendulumPhysicsCore,
    PendulumSimulationResult,
)

from differential_equations.apps.pendulum.renderers.pendulum_matplotlib_renderer import (
    MatplotlibPendulumRenderer,
)

g = 9.81
L = 1.0
MU = .2

X_0=-145
V_0=6.4

FINAL_TIME=40

SOLVER_STEP=0.001


def log(state):
    print(f"--- THE PROGRAM IS AT STATE: {state} ---")

if __name__ == "__main__":

    log("Creating Physics")
    physics = PendulumPhysicsCore(
        g=g,
        L=L,
        mu=MU,
        initial_position=np.deg2rad(X_0),
        initial_velocity=V_0,
    )

    ode = physics.create_ode()

    solver = EulerSolver(
        ode,
        step_size=SOLVER_STEP,
    )

    engine = SimulationEngine(
        solver
    )

    states = engine.run(
        final_time=FINAL_TIME
    )

    log("Simulating Result")

    result = PendulumSimulationResult(
        states=states
    )

    log("Rendering")

    renderer = MatplotlibPendulumRenderer(
        physics=physics,
        result=result,
    )

    # renderer.show()

    renderer.save("pendulum.gif", fps=30)
    # renderer.save("pendulum.html")