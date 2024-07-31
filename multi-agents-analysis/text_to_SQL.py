from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    select,
    insert,
    text
)
from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings

llm = Ollama(model="phi3", request_timeout=360.0)

Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

# Start Create Database Schema

engine = create_engine("sqlite:///:memory:")
metadata_obj = MetaData()

table_name = "city_stats"
city_stats_table = Table(
    table_name,
    metadata_obj,
    Column("city_name", String(16), primary_key=True),
    Column("population", Integer),
    Column("country", String(16), nullable=False),
)
metadata_obj.create_all(engine)
# Finish Create Database Schema

# Start Define SQL Database
sql_database = SQLDatabase(engine, include_tables=["city_stats"])

rows = [
    {"city_name": "Toronto", "population": 2930000, "country": "Canada"},
    {"city_name": "Tokyo", "population": 13960000, "country": "Japan"},
    {
        "city_name": "Chicago",
        "population": 2679000,
        "country": "United States",
    },
    {"city_name": "Seoul", "population": 9776000, "country": "South Korea"},
]
for row in rows:
    stmt = insert(city_stats_table).values(**row)
    with engine.begin() as connection:
        cursor = connection.execute(stmt)

# view current table
stmt = select(
    city_stats_table.c.city_name,
    city_stats_table.c.population,
    city_stats_table.c.country,
).select_from(city_stats_table)

with engine.connect() as connection:
    results = connection.execute(stmt).fetchall()
    print(f"results: {results}")
# Finish Define SQL Database

# --------------------------------
# Part 1: Text-to-SQL Query Engine
query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database, tables=["city_stats"], llm=llm
)
query_str = "Which city has the highest population?"
response = query_engine.query(query_str)

print("\n--------------------------\n")
print(f"Question: {query_str}\n")
print(f"Response: {response}")
