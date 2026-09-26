# VPython Mechanics Simulator

An educational physics and mechanics simulator built with VPython.

This project is developed by Students of the Federal University of Science and Technology of Minas Gerais (UFCI-MG) as part of a extension project by the Physics Department, with the aim of creating interactive simulations to support physics education and outreach activities.

This project was created to support outreach and educational activities in elementary and high schools, providing interactive visualizations of classical mechanics concepts through simple and intuitive simulations.

The goal is to make physics more accessible by allowing students to observe, experiment, and interact with simulations in real time.

## Showcase

![pendulumSim](assets/pendulum.gif)

## Features

- Interactive 3D simulations
- Real-time visualization of physical phenomena
- Educational focus for classroom demonstrations
- Simple and extensible architecture
- Open-source and beginner-friendly codebase

## Planned Problems to Simulate

- Relative motion between two objects
- Ballistics
-

## Technology Stack

- Python 3.12
- VPython
- NumPy
- UV Package Manager

## Requirements

- Python 3.12.x
- UV package manager

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/oenzoribas/vpython-mechanics-simulator.git
   cd vpython-mechanics-simulator
   ```

2. Install UV (if not already installed):

   ```bash
   pip install uv
   ```

   Or follow the official installation guide:

   https://docs.astral.sh/uv/getting-started/installation/

3. Install project dependencies:

   ```bash
   uv sync
   ```

## Running a Simulation

Example:

```bash
uv run python sandbox/free_fall.py
```

## Development Mode

The project includes a development script with automatic reload when source files change:

```bash
dev.bat
```

## Testing the Installation

Verify that VPython is correctly installed:

```bash
uv run python -c "from vpython import *; print('VPython OK')"
```

Expected output:

```text
VPython OK
```

## Educational Purpose

This project is being developed as an educational tool for outreach programs and STEM education initiatives. It aims to help students understand fundamental concepts in physics through interactive experimentation and visualization.

<!-- ## Contributing

Contributions are welcome.

Feel free to open issues, submit pull requests, or propose new simulations and educational features.

## License

This project is licensed under the MIT License. -->
