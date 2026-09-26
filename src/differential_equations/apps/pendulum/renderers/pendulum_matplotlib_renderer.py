import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.ticker import MultipleLocator, FuncFormatter
from fractions import Fraction

from matplotlib.animation import (
    PillowWriter,
    FFMpegWriter,
)

from matplotlib.animation import FuncAnimation
import webbrowser

from differential_equations.apps.pendulum.pendulum_physics_core import (
    PendulumPhysicsCore,
    PendulumSimulationResult,
)


class MatplotlibPendulumRenderer:


    def __init__(
        self,
        physics: PendulumPhysicsCore,
        result: PendulumSimulationResult,
    ) -> None:

        self.physics = physics
        self.result = result

        self.output_dir = (
                Path(__file__).resolve().parent.parent
                / "output"
            )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    @staticmethod
    def _format_radians(
        value: float,
        _,
    ) -> str:

        if np.isclose(value, 0.0):
            return "0"

        fraction = Fraction(
            value / np.pi
        ).limit_denominator(8)

        numerator = fraction.numerator
        denominator = fraction.denominator

        sign = "-" if numerator < 0 else ""
        numerator = abs(numerator)

        if denominator == 1:

            if numerator == 1:
                return rf"${sign}\pi$"

            return rf"${sign}{numerator}\pi$"

        if numerator == 1:
            return rf"${sign}\frac{{\pi}}{{{denominator}}}$"

        return rf"${sign}\frac{{{numerator}\pi}}{{{denominator}}}$"
    
    def _build_animation(
        self,
        n_frames: int = 400,
        interval: int = 20,
        embed_limit_mb: int = 400,
    ):

        
        mpl.rcParams["animation.embed_limit"] = embed_limit_mb

        times = self.result.times
        positions = self.result.positions
        velocities = self.result.velocities

        fig = plt.figure(
            figsize=(14, 8),
            constrained_layout=True
        )

        grid = fig.add_gridspec(
            2,
            2,
            width_ratios=(1.7, 1.0)
        )

        ax_time = fig.add_subplot(
            grid[0, 0]
        )

        ax_phase = fig.add_subplot(
            grid[1, 0]
        )

        ax_pendulum = fig.add_subplot(
            grid[:, 1]
        )

        # ====================================================
        # Limites
        # ====================================================

        x_min = min(positions)
        x_max = max(positions)

        velocity_min = min(velocities)
        velocity_max = max(velocities)

        x_margin = 0.05 * (x_max - x_min)
        velocity_margin = 0.05 * (
            velocity_max - velocity_min
        )

        x_min -= x_margin
        x_max += x_margin

        velocity_min -= velocity_margin
        velocity_max += velocity_margin

        # ====================================================
        # Gráfico temporal
        # ====================================================

        line_position, = ax_time.plot(
            [],
            [],
            label="x(t)"
        )

        line_velocity, = ax_time.plot(
            [],
            [],
            label="v(t)"
        )

        position_point, = ax_time.plot(
            [],
            [],
            "o"
        )

        velocity_point, = ax_time.plot(
            [],
            [],
            "o"
        )

        ax_time.set_xlim(
            min(times),
            max(times)
        )

        ax_time.set_ylim(
            min(
                min(positions),
                min(velocities)
            ),
            max(
                max(positions),
                max(velocities)
            )
        )

        ax_time.set_xlabel("Tempo")
        ax_time.set_ylabel("Estado")

        ax_time.set_title(
            "Solução da EDO - Método de Euler"
        )

        ax_time.grid()
        ax_time.legend()

        # ====================================================
        # Campo vetorial
        # ====================================================

        x_grid = np.linspace(
            x_min,
            x_max,
            150
        )

        velocity_grid = np.linspace(
            velocity_min,
            velocity_max,
            150
        )

        X, V = np.meshgrid(
            x_grid,
            velocity_grid
        )

        Dx, Dvelocity = self.physics.derivative(
            0.0,
            (X, V)
        )

        ax_phase.streamplot(
            X,
            V,
            Dx,
            Dvelocity,
            density=(3.0, 2.0),
            linewidth=0.6,
            arrowsize=0.8
        )

        # ====================================================
        # Diagrama de fase
        # ====================================================

        phase_line, = ax_phase.plot(
            [],
            [],
            linewidth=2,
            label="Trajectory"
        )

        phase_point, = ax_phase.plot(
            [],
            [],
            "o"
        )

        ax_phase.set_xlim(
            x_min,
            x_max
        )

        ax_phase.set_ylim(
            velocity_min,
            velocity_max
        )

        ax_phase.set_xlabel("x (rad)")
        ax_phase.set_ylabel("v")

        ax_phase.xaxis.set_major_locator(
            MultipleLocator(np.pi)
        )

        ax_phase.xaxis.set_major_formatter(
            FuncFormatter(self._format_radians)
        )
        
        ax_phase.set_title("Diagrama de Fase")

        ax_phase.grid()

        # ====================================================
        # Pêndulo
        # ====================================================

        rod, = ax_pendulum.plot(
            [],
            [],
            linewidth=3
        )

        bob, = ax_pendulum.plot(
            [],
            [],
            "o",
            markersize=16
        )

        pivot, = ax_pendulum.plot(
            [0],
            [0],
            "o",
            markersize=8
        )

        ax_pendulum.set_xlim(
            -1.25 * self.physics.L,
            1.25 * self.physics.L
        )

        ax_pendulum.set_ylim(
            -1.25 * self.physics.L,
            1.25 * self.physics.L
        )

        ax_pendulum.set_aspect("equal")

        ax_pendulum.set_xlabel("x")
        ax_pendulum.set_ylabel("y")
        ax_pendulum.set_title("Pêndulo")

        ax_pendulum.grid()

        # ====================================================
        # Atualização
        # ====================================================

        def update(frame: int):

            current_time = times[frame]
            current_pos = positions[frame]
            current_velocity = velocities[frame]

            # -----------------------------------------------
            # Gráfico temporal
            # -----------------------------------------------

            line_position.set_data(
                times[:frame + 1],
                positions[:frame + 1]
            )

            line_velocity.set_data(
                times[:frame + 1],
                velocities[:frame + 1]
            )

            position_point.set_data(
                [current_time],
                [current_pos]
            )

            velocity_point.set_data(
                [current_time],
                [current_velocity]
            )

            # -----------------------------------------------
            # Diagrama de fase
            # -----------------------------------------------

            phase_line.set_data(
                positions[:frame + 1],
                velocities[:frame + 1]
            )

            phase_point.set_data(
                [current_pos],
                [current_velocity]
            )

            # -----------------------------------------------
            # Pêndulo
            # -----------------------------------------------

            bob_x, bob_y = self.physics.bob_position(
                current_pos
            )

            rod.set_data(
                [0, bob_x],
                [0, bob_y]
            )

            bob.set_data(
                [bob_x],
                [bob_y]
            )

            # -----------------------------------------------
            # Títulos
            # -----------------------------------------------

            ax_time.set_title(
                f"Solução da EDO - t = {current_time:.2f}"
            )

            ax_pendulum.set_title(
                f"x = {current_pos:.2f} rad\n"
                f"v = {current_velocity:.2f} rad/s"
            )

            return (
                line_position,
                line_velocity,
                position_point,
                velocity_point,
                phase_line,
                phase_point,
                rod,
                bob
            )

        # ====================================================
        # Animação
        # ====================================================

        frames = np.linspace(
            0,
            len(times) - 1,
            n_frames,
            dtype=int
        )
        
        animation = FuncAnimation(
            fig,
            update,
            frames=frames,
            interval=interval,
            blit=False,
            repeat=False
        )

        return fig, animation

    def save(
        self,
        filename: str,
        fps: int = 30,
        n_frames: int = 400,
        interval: int = 20,
        embed_limit_mb: int = 400,
    ) -> Path:

        fig, animation = self._build_animation(
            n_frames=n_frames,
            interval=interval,
            embed_limit_mb=embed_limit_mb,
        )

        output_path = self.output_dir / filename
        suffix = output_path.suffix.lower()

        if suffix == ".html":
            html = animation.to_jshtml()
            output_path.write_text(
                html,
                encoding="utf-8"
            )

        elif suffix == ".gif":
            animation.save(
                output_path,
                writer=PillowWriter(fps=fps)
            )

        elif suffix == ".mp4":
            animation.save(
                output_path,
                writer=FFMpegWriter(
                    fps=fps,
                    bitrate=3000
                )
            )

        else:
            raise ValueError(
                "Supported formats: .html, .gif, .mp4"
            )

        plt.close(fig)

        return output_path
    
    def show(
        self,
        n_frames: int = 400,
        interval: int = 20,
        filename: str = "pendulum_preview.html",
        embed_limit_mb: int = 400,
    ) -> None:

        fig, animation = self._build_animation(
            n_frames=n_frames,
            interval=interval,
            embed_limit_mb=embed_limit_mb,
        )

        html = animation.to_jshtml()

        output_path = self.output_dir / filename

        page = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Pendulum Simulation</title>
            <style>
                body {{
                    margin: 0;
                    padding: 24px;
                    background: #f5f5f5;
                    font-family: Arial, sans-serif;
                }}

                .simulation {{
                    width: min(1500px, 100%);
                    margin: 0 auto;
                    display: flex;
                    justify-content: center;
                    background: white;
                    padding: 20px;
                    box-sizing: border-box;
                }}
            </style>
        </head>
        <body>
            <main class="simulation">
                {html}
            </main>
        </body>
        </html>
        """

        output_path.write_text(
            page,
            encoding="utf-8"
        )

        plt.close(fig)

        webbrowser.open(
            output_path.resolve().as_uri()
        )