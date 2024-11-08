# Useless Neural Model Generator

## Overview

**NeuralGame** is a simulation in which multiple agents, represented as physical entities, evolve over iterations to improve their fitness, which refers to their ability to perform specific tasks effectively within the environment. This project uses Pygame for visualization and Pymunk for physics simulations. Basic artificial intelligence mechanisms guide the evolution of the agents.

## Features

- **Customizable Agent Evolution**: Neural network-based agent evolution that can be adjusted via various parameters and settings, such as learning rate, mutation rate, and network complexity.
- **Real-time Visualization**: Simulation is visualized in real-time using Pygame.
- **Camera Controls**: Control the camera using arrow keys or by clicking and dragging the mouse.
- **User-friendly GUI**: Start, pause, stop, and load simulations through a simple graphical user interface.

## Prerequisites

To run this project, you need **Python 3.10 or above** installed on your machine. You can download Python from [the official Python website](https://www.python.org/downloads/).

## Installation

1. Clone this repository:

   ```sh
   git clone https://github.com/COMPANYNAMEHERE/NeuralGame.git
   ```

2. Navigate to the project directory:

   ```sh
   cd NeuralGame
   ```

3. (Optional) Install Conda and create a new environment with Python 3.10 (helps manage dependencies and create isolated environments):

   ```sh
   conda create -n NeuralGame python=3.10
   conda activate NeuralGame
   ```

4. Install the required dependencies using pip:

   ```sh
   pip install -r requirements.pip
   ```

## Usage

To start the game, simply run the following command:

```sh
python main.py
```

## TODO

- - **Add Reset Button**: Allow users to quickly reset the simulation.
- **Camera Follow and Zoom Enhancements**: Improve the camera functionality to smoothly follow agents and add zoom capabilities.
  - **Batch Size Configuration**: Allow batch size to be configurable through the GUI or settings file.
  - **Iteration Time Configuration**: Add options to configure iteration time for more customizable simulations.
- **Iteration Time Bugfix**: Fix the bug causing iteration time left to be inaccurate or inconsistent.
- **User-generated Agent Form**: Allow users to create custom agents through a form-based GUI.

## Done
- **Add Record Function**: Implement a recording function to create a timelapse video of the entire generation.

- **Settings Menu**
- **Improved Agent Control**



## Dependencies

To run this project, you need **Python 3.10 or above** installed.

Other dependencies include:

- **cffi**: Version 1.17.1
- **filelock**: Version 3.16.1
- **fsspec**: Version 2024.10.0
- **Jinja2**: Version 3.1.4
- **MarkupSafe**: Version 3.0.2
- **mpmath**: Version 1.3.0
- **networkx**: Version 3.4.2
- **numpy**: Version 2.1.3
- **pycparser**: Version 2.22
- **Pygame**: Version 2.6.1 (Used for game visualization)
- **pygame-ce**: Version 2.5.2
- **pygame-gui**: Version 0.6.12
- **Pymunk**: Version 6.9.0 (Physics engine for agent movement)
- **python-i18n**: Version 0.3.9
- **sympy**: Version 1.13.1
- **PyTorch**: Version 2.5.1 (Used for neural network operations)
- **typing-extensions**: Version 4.12.2

## Author

**Joost van Tiggelen** - [GitHub Profile](https://github.com/COMPANYNAMEHERE)

## License

This project is licensed under the **MIT License**. See the LICENSE file for more details.

