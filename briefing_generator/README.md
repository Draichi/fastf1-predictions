# F1 Text-to-SQL Query Generator

This project demonstrates a text-to-SQL query generator for Formula 1 data using LangChain and OpenAI's language models. It allows users to ask natural language questions about F1 races and drivers, which are then converted into SQL queries and executed against a SQLite database.

## Features

- Natural language to SQL query conversion
- SQL query validation and error correction
- Proper noun lookup for accurate driver names
- Integration with OpenAI's GPT models
- SQLite database interaction
- Retrieval-based tool for driver name suggestions

## Prerequisites

- Python 3.11 or higher
- Conda (for managing Python environments)
- Poetry (for dependency management)
- OpenAI API key
- LangChain API key (optional, for LangSmith integration)

## Installation

1. Clone the repository: `git clone https://github.com/your-username/f1-text-to-sql.git
cd f1-text-to-sql  `

2. Create a new Conda environment: `conda create -n f1-text-to-sql python=3.11
conda activate f1-text-to-sql  `

3. Install Poetry: `curl -sSL https://install.python-poetry.org | python3 -  `

4. Install project dependencies using Poetry: `poetry install .`

5. Create a `.env` file in the project root and add your API keys: `OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_API_KEY=your_langchain_api_key_here  `

## Usage

1. Ensure you have the F1 SQLite database file (`Bahrain_2023_Q.db`) in the `db` directory.

2. Run Jupyter Notebook: `poetry run jupyter notebook  `

3. Open the `langchain_text2SQL.ipynb` notebook and run the cells to interact with the F1 data using natural language queries.

### Gradio Interface

```
poetry run python gradio_sql_agent.py

# dev mode
pymon gradio_sql_agent.py
```

## Project Structure

- `langchain_text2SQL.ipynb`: Main Jupyter notebook containing the text-to-SQL implementation
- `db/Bahrain_2023_Q.db`: SQLite database with F1 race data
- `README.md`: Project documentation (this file)
- `pyproject.toml`: Poetry configuration file for dependency management
- `.env`: Environment file for storing API keys (not tracked in version control)

## Example Queries

- "Who is the fastest driver?"
- "How many fastest laps did Lewis Hamilton achieve?"

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
