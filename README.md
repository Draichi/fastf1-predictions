---
title: Formula 1 AI
emoji: 🏎️
colorFrom: red
colorTo: yellow
sdk: gradio
sdk_version: 5.4.0
app_file: app.py
pinned: true
license: mit
short_description: Chat with the telemetry databases from Formula 1 races
python_version: 3.11
suggested_hardware: cpu-basic
tags: ["formula1", "telemetry", "sql", "agent", "llm", "data analysis"]
---

# Formula 1 AI 🏁

Formula 1 Report Generator is an innovative project aimed at generating reports from Formula 1 telemetry data. Accurate lap time predictions are crucial in Formula 1 as they can influence strategic decisions during races, qualifying, and practice sessions. By leveraging advanced machine learning algorithms and a **ReAct Agent implemented in `app.py`**, FastF1 Predictions seeks to provide precise and reliable predictions to enhance the competitive edge of teams and drivers.

<video src="assets/demo.mp4" controls></video>

Deployed on 🤗 [Hugging Face](https://huggingface.co/spaces/Draichi/Formula1-race-debriefing).

## Purpose

The primary goal of FastF1 Predictions is to utilize historical race data and telemetry to forecast lap times. This predictive capability can aid in optimizing race strategies, making informed decisions on tire changes, and evaluating driver performance. The project employs machine learning techniques, specifically Random Forest and Gradient Boosted Decision Trees, to build robust predictive models.

## Project Structure

Currently, the project includes:

- **app.py**: The main application file implementing the **ReAct Agent** for interacting with telemetry data.
- **regression-models/**:
  - **[sector-3-time-prediction.ipynb](./regression-models/sector-3-time-prediction.ipynb)**: A demonstration notebook showcasing how to use the algorithms to predict lap times based on historical telemetry data.

Future updates will expand the repository with more resources, including additional notebooks, scripts, and enhanced functionalities.

## Setup Instructions

To get started with Formula 1 AI, follow these steps:

### Prerequisites

Ensure you have Python installed (version 3.11).

### Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/Draichi/formula1-ai.git
   cd formula1-ai
   ```

2. Create a virtual environment:

   ```sh
   # Using Conda (recommended)
   conda env create -n formula1-ai python=3.11

   conda activate formula1-ai
   ```

3. Install the dependencies:

   ```sh
   poetry install
   ```

### Running the App

1. Start the application in development mode:

   ```sh
   pymon app.py
   ```

### Running the Notebook

1. Launch Jupyter Notebook:

   ```sh
   jupyter
   ```

2. Open `sector-3-time-prediction.ipynb` and run the cells to see the lap time prediction in action.

## Vision for the Future

The potential for FastF1 Predictions is immense. As we continue to gather more data and refine our models, we aim to incorporate additional data sources such as weather conditions. Moreover, we plan to explore advanced modeling techniques, including deep learning, Agent LLM and reinforcement learning methods, to further enhance prediction accuracy.

Stay tuned for updates, and thank you for your support!

---

Feel free to reach out if you have any questions or need further assistance. Happy predicting!
