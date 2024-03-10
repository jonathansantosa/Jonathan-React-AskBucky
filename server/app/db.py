import chromadb

chroma_client = chromadb.HttpClient(host="localhost", port=8000)

#################### Utility Functions ####################
    
def reset_client():
    chroma_client.reset()

def pulse_client():
    chroma_client.heartbeat()

#################### Collection Functions #########s###########

def list_all_collections():
    chroma_client.list_collections()

def get_or_create_collection(name):
    collection = chroma_client.get_or_create_collection(name)
    return collection

def delete_collection(name):
    chroma_client.delete_collection(name)

def rename_collection(collection : chromadb.Collection, new_collection_name):
    collection.modify(new_collection_name)

def count_collection(collection : chromadb.Collection):
    return collection.count()

def add_or_update_collection(collection : chromadb.Collection, embeddings : list, metadatas, documents, ids):
    collection.add(
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents,
        ids=ids
    )