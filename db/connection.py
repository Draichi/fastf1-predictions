from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri("sqlite:///db/Bahrain_2023_Q.db")
