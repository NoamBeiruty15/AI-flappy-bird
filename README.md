# AI Flappy Bird

AI Flappy Bird, a Python-based implementation of the classic Flappy Bird game, enhanced with an AI component using NEAT (NeuroEvolution of Augmenting Topologies). The AI learns to play the game through evolution, improving its performance over generations.

![Example of the A.I birds in action](images/Birds_In_Action.png)

![Video example of the A.I birds in action](videos/Birds_In_Action.mov)

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
- [Dependencies](#dependencies)
- [File Structure](#file-structure)

## Features

- **AI Player**: Uses NEAT to evolve neural networks that control the bird.
- **User Player**: Uses space bar to jump the user controls the bird.
- **User Interface**: Pygame-based UI with smooth graphics and animations.
- **Dynamic Environment**: Pipes spawn randomly, making the game more challenging.
- **Score Tracking**: Keeps track of the score based on pipes passed.

## Getting Started

To run this project, you'll need Python installed on your machine, along with the necessary dependencies.

### Dependencies

Make sure you have the following installed:

- Python 3.x
- Pygame library
- NEAT-Python library

1. In your terminal install:
```bash
   pip install pygame
   pip install neat-python 
```
### Installation

2. Clone the repository:
   ```bash
   git clone https://github.com/NoamBeiruty15/AI-flappy-bird
```
## File Structure

```plaintext
AI-flappy-bird/
│
├── AI_flappy_bird.py      # Main game logic and AI integration
├── flappy_bird.py         # Normal flappy bird for a user to play
├── neat-config.txt        # Configuration for NEAT
├── images/                # Folder containing game images
    ├── bird1.png          # Bird image
    ├── bg.png             # Background image
    ├── base.png           # Base image
    └── pipe.png           # Pipe image
