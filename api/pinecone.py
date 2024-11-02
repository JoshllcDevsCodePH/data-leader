import os
import time
from pinecone import Pinecone as PineconeClient, ServerlessSpec

class Pinecone:
    def __init__(self):
        self.client = PineconeClient(api_key=os.getenv("PINECONE_API_KEY"))  # Set your API key

    def existing_indexes(self):
        return [index_info["name"] for index_info in self.client.list_indexes()]

    def create_index(self, name):
        self.client.create_index(
            name=name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-west-2"
            )
        )
        while not self.client.describe_index(name).status['ready']:
            time.sleep(1)

    def upsert(self, idx, data):
        if idx not in self.existing_indexes():
            self.create_index(idx)
        index = self.client.Index(idx)
        return index.upsert(vectors=data, namespace="main")

    def query(self, idx, vector_data, filter={}, n=10):
        index = self.client.Index(idx)
        return index.query(
            vector=vector_data,
            filter=filter,
            top_k=n,
            include_metadata=True
        )

    def delete_index(self, idx):
        self.client.delete_index(idx)

# Example usage:
# pinecone_instance = Pinecone()
# result = pinecone_instance.upsert("example_index", [{"id": "Grease", "values": [0.1]*1536, "metadata": {"genre": "comedy", "year": 2020}}])
# print(result)
