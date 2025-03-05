
<p align="center">
<img src="./assets/robot-holding-camera.png" width="720">
</p>


<h4 align="center">🤘🤖🤘 Build actual ai-powered robots for yourself now.</h4>

<p align="center">
  <img src="https://img.shields.io/badge/Version-0.1.0-limegreen">
  <a href="https://ko-fi.com/jonathanshulgach">
    <img src="https://img.shields.io/badge/$-donate-ff69b4.svg?maxAge=2592000&amp;style=flat">
  </a>
</p>

<p align="center">
  <a href="#about">Intro</a> •
  <a href="#getting-started">Getting Started</a> •
  <a href="#installation">Installation</a>
</p>

## About 

NeuroBridge is an AI-powered modular server designed for robotic control, vision processing, and LLM-based interactions. It integrates LLM-powered decision-making, real-time perception, and modular execution of AI-driven skills like object detection, voice interaction, and task automation.

🚀 Features:

- LLM Integration 🧠: Handles natural language interactions and command execution.
- AI-Powered Vision 👁️: Camera and object detection with Grounding DINO.
- Task Automation 🤖: Executes robotic actions via a structured AI skills system.
- Modular Architecture ⚡: Components for messaging, skills, and perception are neatly separated.
- Real-time Control 🎛️: Async message handling and AI-driven automation.
🔧 Built with: Python, OpenCV, Groq LLM API, asyncio, threading, and modular AI components.

## Getting Started

The `config.yaml` file contains hyperparameters to load with the AI server. Adjust these according to your preferences.

## Installation

1. Create a virtual environment using [Anaconda](https://www.anaconda.com/products/distribution) or Python's virtualenv
   - Using Anaconda:
      ~~~
      conda create -n ephys
      conda activate ephys
      ~~~
   - Using Python's virtualenv:
     ~~~
     python3 -m venv .ephys
     source .ephys/bin/activate # Linux
     call .ephys/Scripts/activate # Windows
     ~~~
2. Clone the repository and navigate to the project directory
   ~~~
   git clone https://github.com/JShulgach/NeuroBridge.git
   cd NeuroBridge
   ~~~
3. Install dependencies
    ~~~
    pip install -r requirements.txt
    ~~~

## Demo

To run the AI server, execute the following command:
```bash
python main.py --enable_tts true --enable_camera true
```

You can now type into the terminal and converse with the NeuroBridge AI! Try it for yourself and see how it behaves...
<p align="center">
<img src="./assets/terminal_first_test.jpg" width="720">
</p>

