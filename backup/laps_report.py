from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    select,
    column,
)
import os
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core import SQLDatabase
from llama_index.llms.ollama import Ollama
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
)
from llama_index.core.indices.struct_store import SQLTableRetrieverQueryEngine
from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "title": "bold white on orchid1",
    "text": "dim chartreuse1",
})

console = Console(theme=custom_theme)

Settings.llm = Ollama(model="phi3", request_timeout=360.0)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

engine = create_engine("sqlite:///multi-agents-analysis/data/laps.db")
metadata_obj = MetaData()

sql_database = SQLDatabase(engine)

# manually set extra context text
city_stats_text = """This table gives information regarding the performance in a race about each driver.
The time is split into 3 different sectors.
The speed is split into SpeedI1, SpeedI2, SpeedFL and SpeedST"""

table_node_mapping = SQLTableNodeMapping(sql_database)
table_schema_objs = [
    (SQLTableSchema(table_name="laps", context_str=city_stats_text))
]

obj_index = ObjectIndex.from_objects(
    table_schema_objs,
    table_node_mapping
)

query_engine = SQLTableRetrieverQueryEngine(
    sql_database, obj_index.as_retriever(similarity_top_k=1)
)
response = query_engine.query("Which driver had the lowers time in sector 1?")
print(response)
