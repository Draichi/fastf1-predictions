from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from rich.console import Console
from rich.theme import Theme
from rich import print
import logging
import sys
import os.path
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

custom_theme = Theme({
    "title": "bold white on orchid1",
    "text": "dim chartreuse1",
})
console = Console(theme=custom_theme)

# bge-base embedding model
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

# ollama
Settings.llm = Ollama(model="phi3", request_timeout=360.0)

# check if storage already exists
PERSIST_DIR = "./storage"
if not os.path.exists(PERSIST_DIR):
    # load the documents and create the index
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    # store it for later
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    # load the existing index
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)


# query your data
query_engine = index.as_query_engine()


queries = [
    "O que o autor fez enquanto estava crescendo?",
    "Liste as principais características do autor"
]

for query in queries:
    console.print(query, style="title")
    response = query_engine.query(query)
    print(
        f"[italic chartreuse1 on grey7]{response}[/italic chartreuse1 on grey7]\n")
