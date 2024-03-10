##################################### Imports #####################################

# import chromadb
import pandas as pd
import numpy as np
import openai
import json
import tiktoken
import time
from tqdm import tqdm
import hnswlib
import random
import os
import app.db as my_chroma_db

##################################### Clients #####################################

openai_client = openai.OpenAI(api_key="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")
# chroma_client = chromadb.PersistentClient(path="data/chroma_client")

##################################### Globals #####################################

DATAFILE_PATH = "/Users/joshua/dev/askbucky/server/scrape/data/bulletin/output.json"
EMBEDDINGS_PATH = "/Users/joshua/dev/askbucky/server/scrape/data/bulletin/embeddings.json"

EMBEDDING_MODEL = "text-embedding-ada-002"
TOKENIZER_MODEL = "cl100k_base"
TEXTGEN_MODEL = "gpt-3.5-turbo"

MAX_TOKEN_COUNT = 1000

# COLLECTION = collection = chroma_client.get_or_create_collection("chroma_client")

DATA_CHUNK_COUNT = 10

##################################### Utility Functions #####################################

# Use chroma as vector store, as oppose to file reading

def count_tokens(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def sublist_tokenizer_encodings(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

##################################### Data Formatting Functions #####################################

def trim_data(datafile):
    with open(datafile, 'r') as df:
        json_output = list(json.load(df)) # this is a list
    
    updated = []
    for dict_index in range(len(json_output)):
        block = json_output[dict_index]
        block_content = block["content"] # contains h1, h2 headers
        block_content_keys = list(block_content.keys())
        for block_content_key in block_content_keys:
            if block_content_key.startswith('p'):
                if str(block_content[block_content_key]).strip() == "":
                    del block_content[block_content_key]
            else:
                header_dict = block_content[block_content_key]
                header_content = header_dict["content"] # contains h3, paragraphs
                header_content_keys = list(header_content.keys())
                for h3_p_ul in header_content_keys:
                    data = header_content[h3_p_ul]
                    if isinstance(data, str): # h3 or p
                        if str(data).strip() == "":
                            del header_content[h3_p_ul]
                    if isinstance(data, list): # converts ul to a string
                        data = list(filter(None, data))
                        paragraph = " [__start context__] [The following is a list whose elements are separated by semicolons] [__end context__]"
                        if data:
                            paragraph += ";".join(data)
                        header_content[h3_p_ul] = paragraph
                            
        updated.append(block)
    
    updated_json = json.dumps(updated, indent=2)
    with open(datafile, 'w') as df:
        df.write(updated_json)
    return updated_json

def contextualize(datafile):
    with open(datafile, 'r') as df:
        json_output = list(json.load(df))
    
    updated = []
    for dict_index in range(len(json_output)):
        block = json_output[dict_index]
        block_url = block["url"]
        block_content = block["content"] # contains h1, h2 headers
        block_content_keys = list(block_content.keys())
        block_context = f"The following paragraph is found on {block_url} , under "
        h1_header_context = ""
        h2_header_context = ""
        for block_content_key in block_content_keys:
            if block_content_key.startswith('p'):
                existing_content = block_content[block_content_key]
                p_context = f"The following paragraph is found on {block_url}. "
                block_content[block_content_key] = "{}{}{}{}".format("[__start context__] ", p_context, "[__end context__] ", existing_content)
            else:
                header_dict = block_content[block_content_key]
                header_header = header_dict["header"]
                if block_content_key.startswith("h1"):
                    h1_header_context = f"h1 header: {header_header}; "
                if block_content_key.startswith("h2"):
                    h2_header_context = f"h2 header: {header_header}; "
                header_content = header_dict["content"]
                header_content_keys = list(header_content.keys())
                header3_context = ""
                prev_h3_p_ul = None
                for h3_p_ul in header_content_keys:
                    data = header_content[h3_p_ul]
                    if isinstance(data, str):
                        if h3_p_ul.startswith("h3"):
                            header3_context = f"h3 header: {header_content[h3_p_ul]}; "
                        if h3_p_ul.startswith("p"):
                            data = "{}{}{}{}{}{}{}".format("[__start context__] ", block_context, h1_header_context, h2_header_context, header3_context, "[__end context__] ", data)
                        if h3_p_ul.startswith("ul"):
                            if prev_h3_p_ul:
                                if isinstance(header_content[prev_h3_p_ul], str) and prev_h3_p_ul.startswith('p'):
                                    prev_content = header_content[prev_h3_p_ul]
                                    header_content[prev_h3_p_ul] = "{}{}".format(prev_content, header_content[h3_p_ul])
                        header_content[h3_p_ul] = data
                    prev_h3_p_ul = h3_p_ul
        
        updated.append(block)
    
    updated_json = json.dumps(updated, indent=2)
    with open(datafile, 'w') as df:
        df.write(updated_json)
    return updated_json

def get_embedding(content):
        try:
            embedding = openai_client.embeddings.create(
                input=str(content),
                model=EMBEDDING_MODEL
            ).data[0].embedding
            return embedding
        except Exception as e:
            print(e)

def chroma_embed(datafile, collection):
    with open(datafile, 'r') as df:
        json_output = list(json.load(df))
    
    id = 0
    with tqdm(total=len(json_output), desc=f"adding to chroma collection...") as pbar:
        for json_dict_index in range(len(json_output)):
            json_dict = json_output[json_dict_index]
            metadatas = {} # chroma metadatas
            existing_content = '' # chroma document
            metadatas['url'] = json_dict['url']
            json_dict_content = json_dict['content']
            json_dict_content_keys = list(json_dict_content.keys())
            for json_dict_content_key in json_dict_content_keys:
                
                header_dict = json_dict_content[json_dict_content_key]
                if json_dict_content_key.startswith('h1'):
                    metadatas['h1'] = header_dict['header']
                if json_dict_content_key.startswith('h2'):
                    metadatas['h2'] = header_dict['header']
                header_dict_content = header_dict['content']
                header_dict_content_keys = list(header_dict_content.keys())
                
                for h3_p_ul in header_dict_content_keys:
                    data = header_dict_content[h3_p_ul]
                    if isinstance(data, str):
                        if h3_p_ul.startswith('h3'):
                            metadatas['h3'] = data
                        elif h3_p_ul.startswith('p') or h3_p_ul.startswith('ul'):
                            existing_content = data
                            embedding = get_embedding(existing_content)
                            id += 1
                            doc_id = f"doc{id}"
                            my_chroma_db.add_or_update_collection(collection=collection, embeddings=embedding, metadatas=metadatas, documents=existing_content, ids=doc_id)
            pbar.update()

def fetch(source: list[str]) -> str:
    with open(DATAFILE_PATH, 'r') as df:
        json_output = list(json.load(df))
    
    with tqdm(total=len(json_output), desc=f"Fetching content from source: {source[0]}; {source[1]}") as pbar:
        for dict_index in range(len(json_output)):
            block = json_output[dict_index]
            if block["url"] == source[0]:
                block_content = block["content"]
                block_content_keys = list(block_content.keys())
                for block_content_key in block_content_keys:
                    if block_content_key.startswith('p') or block_content_key.startswith('ul'):
                        if block_content_key == source[1]:
                            existing_content = block_content[block_content_key]
                            return existing_content
                    else: 
                        header_dict = block_content[block_content_key]
                        header_content = header_dict["content"]
                        header_content_keys = list(header_content.keys())
                        for h3_p_ul in header_content_keys:
                            if h3_p_ul.startswith('p') and h3_p_ul == source[1]:
                                existing_content = header_content[h3_p_ul]
                                return existing_content
            pbar.update()
    
    return f"Invalid source: {source}"

##################################### Generator Functions #####################################

'''
Generates embeddings to a given datafile. Costs $0.09 per run.
'''
def generate_embeddings(datafile):
    with open(datafile, 'r') as df:
        json_output = list(json.load(df))

    embeddings_data = []

    with tqdm(total=len(json_output), desc=f"Generating embeddings for {datafile}") as pbar:
        for dict_index in range(len(json_output)):
            block = json_output[dict_index]
            block_content = block["content"]
            embeddings_dict = {}
            embeddings_dict["url"] = block["url"]
            embeddings_dict["embeddings"] = {}
            block_content_keys = list(block_content.keys())
            for block_content_key in block_content_keys:
                if block_content_key.startswith('p') or block_content_key.startswith('ul'):
                    existing_content = block_content[block_content_key]
                    existing_content_embedding = get_embedding(existing_content)
                    embeddings_dict["embeddings"][block_content_key] = existing_content_embedding
                else:
                    header_dict = block_content[block_content_key]
                    header_content = header_dict["content"]
                    header_content_keys = list(header_content.keys())
                    for h3_p_ul in header_content_keys:
                        if h3_p_ul.startswith('p'):
                            existing_content = header_content[h3_p_ul]
                            existing_content_embedding = get_embedding(existing_content)
                            embeddings_dict["embeddings"][h3_p_ul] = existing_content_embedding
            embeddings_data.append(embeddings_dict)
            pbar.update()
    
    json_str = json.dumps(embeddings_data, indent=2)
    with open(EMBEDDINGS_PATH, 'w') as ef:
        ef.write(json_str)
    return json_str

'''
Generates a context for a given query using Heirarchical Navigable Small World graphs

@param M                - the number of bi-directional links created for every new element during construction. 
                            Reasonable range for M is 2-100. Higher M work better on datasets with high intrinsic 
                            dimensionality and/or high recall, while low M work better for datasets with low intrinsic 
                            dimensionality and/or low recalls. The parameter also determines the algorithm's memory 
                            consumption, which is roughly M * 8-10 bytes per stored element. As an example for dim=4 
                            random vectors optimal M for search is somewhere around 6, while for high dimensional 
                            datasets (word embeddings, good face descriptors), higher M are required (e.g. M=48-64) 
                            for optimal performance at high recall. The range M=12-48 is ok for the most of the use 
                            cases. When M is changed one has to update the other parameters. Nonetheless, ef and 
                            ef_construction parameters can be roughly estimated by assuming that M*ef_{construction} 
                            is a constant.

@param ef_construction  - the parameter has the same meaning as ef, but controls the index_time/index_accuracy. 
                            Bigger ef_construction leads to longer construction, but better index quality. At some 
                            point, increasing ef_construction does not improve the quality of the index. One way to 
                            check if the selection of ef_construction was ok is to measure a recall for M nearest 
                            neighbor search when ef =ef_construction: if the recall is lower than 0.9, than there is 
                            room for improvement.
'''
def generate_context_hnsw(query, m=16, ef_constr=200, test=False):
    similarities = {}
    query_vector = get_embedding(query)

    file_path = EMBEDDINGS_PATH
    with open(file_path, 'r') as file:
        embeddings = json.load(file)
    
    # NOTE: May need to change when data/.../embeddings.json is modified
    dims = len(embeddings[1]['embeddings']['p_paragraph_1'])

    # Create and initialize a new HNSW index
    hnsw_index = hnswlib.Index(space='cosine', dim=dims)
    hnsw_index.init_index(max_elements = 10000, ef_construction = ef_constr, M = m)

    similarities_embeddings = {}

    with tqdm(total=len(embeddings), desc=f"Generating similarities dictionary for HNSW") as pbar:
        i = 0
        ls = []
        for block in embeddings:
            url = block["url"]
            paragraph_embeddings = block["embeddings"]
            for paragraph in paragraph_embeddings:
                key = "{}{}{}".format(url, ";", paragraph)
                similarities_embeddings[i] = [key, paragraph_embeddings[paragraph]]
                ls.append(paragraph_embeddings[paragraph])
                i += 1
            pbar.update()

    hnsw_index.add_items(ls)

    # Control recall by setting ef (which should always be > k, the number of closest elements)
    hnsw_index.set_ef(DATA_CHUNK_COUNT + 5)

    # Fetch k nearest neighbors
    labels, distances = hnsw_index.knn_query(query_vector, k=DATA_CHUNK_COUNT)
    context = ""
    for i in labels[0]:
        key = similarities_embeddings[i][0]
        source = str(key).split(sep=";")
        if not test:
            source_data = fetch(source)
            context += f"Data chunk {i + 1}: {source_data}; "

    return context

'''
Generates a response to a given query and context using OpenAI's API
'''
def generate_response(query, context):
    # SYSTEM PROMPT
    request = [
        {"role": "system", "content": "You are a personalized assistant for students at Santa Clara University (SCU), designed to communicate conversationally and guide them through SCU's extensive online resources. Students often have specific queries related to course selection, such as prerequisites, professor ratings, course content, and scheduling, but may not know where to find this information among SCU's vast web resources. Your task is to assist by analyzing data chunks marked by [start context] and [end context], extracting and summarizing key information to answer students' questions comprehensively. Consider individual preferences, academic backgrounds, and career goals to tailor your recommendations. Provide detailed, easy-to-understand responses, including the URL(s) of your sources. Encourage further questions to ensure clarity and satisfaction, and ask for feedback to improve future assistance."},
        {"role": "user", "content": "Student's Question: " + query},
        {"role": "user", "content": "Context: " + context}
    ]
    token_count = count_tokens(request[2].get("content"), TOKENIZER_MODEL)
    # OPENAI CALL
    begin_call = time.time()
    response = openai_client.chat.completions.create(
        model=TEXTGEN_MODEL,
        messages=request,
        temperature=0.1,
        max_tokens=1100,
    ).choices[0].message.content
    end_call = time.time()
    print("\nOpenAI call took {:.2f} seconds to execute.\n".format(end_call - begin_call))
    return response

'''
DEPRECATED: Generating context from a given query - brute force
'''
def generate_context(query, test=False):
    similarities = {}
    query_vector = get_embedding(query)

    file_path = EMBEDDINGS_PATH
    with open(file_path, 'r') as file:
        embeddings = json.load(file)
    
    with tqdm(total=len(embeddings), desc=f"Generating similarities dictionary") as pbar:
        for block in embeddings:
            url = block["url"]
            paragraph_embeddings = block["embeddings"]
            for paragraph in paragraph_embeddings:
                key = "{}{}{}".format(url, ";", paragraph)
                similarities[key] = np.dot(query_vector, paragraph_embeddings[paragraph])
            pbar.update()
    
    series = pd.Series(similarities, dtype=np.float64)
    sorted_series = series.sort_values(ascending=False)
    top_results = sorted_series.head(DATA_CHUNK_COUNT).to_dict()
    
    context = ""
    for i, key in enumerate(top_results):
        source = str(key).split(sep=";")
        if not test:
            source_data = fetch(source)
            context += f"Data chunk {i + 1}: {source_data}; "
    return context

##################################### Main Executable #####################################

def run(query):
    context = generate_context(query)
    # print(context)
    response = generate_response(query, context)
    return response

if __name__ == "__main__":
    # The first time you are running this program, please do the following:
    # READ ALL STEPS BEFORE PERFORMING THEM!

    # 1. Open a VSCode terminal and navigate to: askbucky/server/scrape
    # 1b. Ensure that there exists a folder, under askbucky/server/scrape, called "data". If not, create one.
    # 1c. Ensrue that there exists a folder, under askbucky/server/scrape/data, called "bulletin". If not, create one.
    # 2. Run the following command: python recurse.py
    #   -- note that based on your computer, the "python" command may be "python3" --
    # 3. Step 2 should generate a file called "output.json". Verify it exists here: askbucky/server/scrape/data/bulletin/output.json
    # 4. Now, un-comment the 3 lines of code in "PART A", located below. Also, comment EVERYTHING below "PART B"
    # 5. In the VSCode terminal window, run the following command: python rag.py
    #   -- note that based on your computer, the "python" command may be "python3" --
    # 6. This process should take <=1hr 30min. It is generating a file 10.9 MILLION lines long! (yes really)
    # 7. Comment the 3 lines of code in "PART A", located below. Also, un-comment EVERYTHING below "PART B"

    # All the steps above are a one time process for our data set. From now on, you can run steps 8-11 without re-running steps 1-7.

    # 8. Change the query variable to a question of your choosing.
    # 9. Run the following command in a VSCode terminal: python rag.py
    #   -- note that based on your computer, the "python" command may be "python3" --
    # 10. Observe the result. Tweak the system prompt and/or openai call, re-run, and observe how the result changes.
    #   -- you can find the system prompt and openai call in the "generate_response()" function. This should be on line 233.
    #   -- you can also find it by searching (ctr/cmd f) for "# SYSTEM PROMPT" or "# OPENAI CALL"

    ########## PART A ##########
    trim_data(DATAFILE_PATH)
    # contextualize(DATAFILE_PATH)
    # generate_embeddings(DATAFILE_PATH)

    my_chroma_db.delete_collection('SCU_Undergraduate_Bulletin_2023-2024')
    collection = my_chroma_db.get_or_create_collection('SCU_Undergraduate_Bulletin_2023-2024')
    chroma_embed(DATAFILE_PATH, collection)

    ########## PART B ##########
    query = "Hello!"
    print(f"Query:\t{query}\n")
    print(run(query))

    ########## METRICS ##########
    # queries = [
    #     'Tell me what COEN 140 and 163 are about.', 
    #            ]
    # hnsw_times = []
    # dot_times = []
    # for query in queries:
    #     st = time.time()
    #     generate_context(query, test=True)
    #     et = time.time()
    #     dot_times.append(et-st)
    #     st = time.time()
    #     generate_context_hnsw(query, test=True)
    #     et = time.time()
    #     hnsw_times.append(et-st)
        
    # print(f'\nAverage HNSW contextualization time:\n')
    # print(f'{str(1.0*sum(hnsw_times)/len(hnsw_times))} seconds')
    # print(f'\nAverage Dot Product contextualization time:\n')
    # print(f'{str(1.0*sum(dot_times)/len(dot_times))} seconds')
    # print()

    ########## Count tokens in DATAFILE ##########
    # with open(DATAFILE_PATH, 'r') as dp:
    #     json_data = str(json.load(dp))
    #     print(count_tokens(json_data, TOKENIZER_MODEL))