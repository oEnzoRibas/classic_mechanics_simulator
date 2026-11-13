# Two Trains and a Bird: Motion Simulation

This Python project visualizes a classic mechanics problem involving two trains and a bird.

Two trains travel toward each other on the same straight track. They start 60 km apart, and each train moves at 30 km/h. At the moment they begin approaching one another, a bird leaves the front of one train and flies toward the other at 60 km/h. Every time the bird reaches a train, it turns around and flies toward the other train. The trains continue moving until they collide.

The problem asks: **How far does the bird travel before the trains collide?**

The simulation lets you watch the motion and explore how changing the trains’ and bird’s speeds affects the result. It includes a 3D view, a graph of the positions over time, adjustable speeds, and a flashcard that reveals the original problem and its solution step by step.

## Features

- 3D animation of the trains and bird
- Position-versus-time graph
- Side and overhead camera views
- Controls to start, pause, and reset the simulation
- Editable speeds for both trains and the bird
- Flashcard with the problem statement and a step-by-step solution

## Requirements

- Python 3
- VPython

## Installation

Install the required library:

    python -m pip install -r requirements.txt

## Run the simulation

    python passaroOFC.py