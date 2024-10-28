# LLM Multi Agent Race Analysis System

This project utilizes a multi-agent system to analyze race data from the FastF1 library using CrewAI and LangChain. The system is designed to provide detailed insights and comparisons between drivers in a race session.

## Setup Instructions

1. **Create and activate a Conda virtual environment:**

   ```sh
   conda create --name race-analysis python=3.11
   conda activate race-analysis
   ```

2. **Install the dependencies:**

   ```sh
   conda env create --file environment.yml
   ```

3. **Paste your OpenAI key in the .env file.**

4. **Provide basic context for the analysis system:**

   - Create a file named `context.md` in the root directory.
   - Add a brief text in `context.md` to provide basic context to the analysis system.

5. **Run the main script to start the race analysis:**
   ```sh
   python main.py
   ```

## Usage

To run the analysis, execute the following command:
