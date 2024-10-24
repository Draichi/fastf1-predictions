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
import logging
import sys
from llama_index.core import SQLDatabase, VectorStoreIndex
from llama_index.core.query_engine import NLSQLTableQueryEngine, RetrieverQueryEngine
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_index.core.retrievers import NLSQLRetriever
from llama_index.core.indices.struct_store.sql_query import (
    SQLTableRetrieverQueryEngine,
)
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
)
from rich import print


llm = Ollama(model="phi3", request_timeout=360.0)

Settings.llm = llm

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
# stmt = select(
#     city_stats_table.c.city_name,
#     city_stats_table.c.population,
#     city_stats_table.c.country,
# ).select_from(city_stats_table)

# with engine.connect() as connection:
#     results = connection.execute(stmt).fetchall()
#     print(f"results: {results}")
# Finish Define SQL Database

# --------------------------------
# Part 1: Text-to-SQL Query Engine
# query_engine = NLSQLTableQueryEngine(
#     sql_database=sql_database, tables=["city_stats"], llm=llm
# )
# query_str = "Which city has the highest population?"
# response = query_engine.query(query_str)

# print("\n-----------Part 1---------------\n")
# print(f"Question: {query_str}\n")
# print(f"Response: {response}")

# --------------------------------
# Part 2: Query-Time Retrieval of Tables for Text-to-SQL

# set Logging to DEBUG for more detailed outputs
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# manually set context text
# city_stats_text = (
#     "This table gives information regarding the population and country of a"
#     " given city.\nThe user will query with codewords, where 'foo' corresponds"
#     " to population and 'bar' corresponds to city."
# )

# table_node_mapping = SQLTableNodeMapping(sql_database)
# table_schema_objs = [
#     (SQLTableSchema(table_name="city_stats", context_str=city_stats_text))
# ]  # add a SQLTableSchema for each table

# obj_index = ObjectIndex.from_objects(
#     table_schema_objs,
#     table_node_mapping,
#     VectorStoreIndex,
# )

# query_engine = SQLTableRetrieverQueryEngine(
#     sql_database, obj_index.as_retriever(similarity_top_k=1, llm=llm)
# )
# query_str = "Which city has the highest population?"
# response = query_engine.query(query_str)
# print("[dark_magenta on grey7]\n\n---------Part 2-----------------\n[/dark_magenta on grey7]")
# print(f"[chartreuse3 on grey7]Question: {query_str}[/chartreuse3 on grey7]\n")
# print(
#     f"[bold chartreuse1 on grey7]Response: {response}[/bold chartreuse1 on grey7]\n")
# print(
#     f"[chartreuse3 on grey7]metadata: {response.metadata}[/chartreuse3 on grey7]\n")


# --------------------------------
# Part 3: Text-to-SQL Retriever
"""
    So far our text-to-SQL capability is packaged in a
    query engine and consists of both retrieval and synthesis.

    You can use the SQL retriever on its own.
    We show you some different parameters you can try,
    and also show how to plug it into our RetrieverQueryEngine
    to get roughly the same results.
"""


# default retrieval (return_raw=True)
nl_sql_retriever = NLSQLRetriever(
    sql_database, tables=["city_stats"], return_raw=True
)

# results = nl_sql_retriever.retrieve(
#     "Return the top 5 cities (along with their populations) with the highest population."
# )

# print(len(results))
# for n in results:
#     print(
#         f"[bold chartreuse1 on grey7]> n: {n.metadata}[/bold chartreuse1 on grey7]\n")

"""
    # Plug into our RetrieverQueryEngine

    We compose our SQL Retriever with our standard RetrieverQueryEngine 
    to synthesize a response. The result is roughly similar 
    to our packaged Text-to-SQL query engines.
"""

query_engine = RetrieverQueryEngine.from_args(nl_sql_retriever)

response = query_engine.query(
    "Return the top 5 cities (along with their populations) with the highest population."
)

print(
    f"[bold chartreuse1 on grey7]> Response: {str(response)}[/bold chartreuse1 on grey7]\n")
""""
> Response:  Tokyo - 13,960,000
Seoul - 9,776,000
Toronto - 2,930,000
Chicago - 2,679,000
"""
