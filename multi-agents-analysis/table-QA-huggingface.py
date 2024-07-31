from transformers import pipeline
import pandas as pd

# prepare table + question
data = {"Actors": ["Brad Pitt", "Leonardo Di Caprio",
                   "George Clooney"], "Number of movies": ["87", "53", "69"]}
# table = pd.DataFrame.from_dict(data)
query = "how many movies does Leonardo Di Caprio have?"
# data = {
#     "year": [1896, 1900, 1904, 2004, 2008, 2012],
#     "city": ["athens", "paris", "st. louis", "athens", "beijing", "london"]
# }
tablle = pd.DataFrame.from_dict(data)
# query = "when london had the olympics game?"


# pipeline model
# Note: you must to install torch-scatter first.
tqa = pipeline(task="table-question-answering",
               model="google/tapas-large-finetuned-wtq")

# result
result = tqa(table=tablle, query=query)
print(f"Result: {result}")

print(f"\nResponse: {result['cells'][0]}")
# 53
