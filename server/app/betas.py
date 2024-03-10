from dotenv import dotenv_values
import hnswlib
import json
import numpy as np
from openai import OpenAI
import pandas as pd
import time
from tqdm import tqdm

##################################### GLOBALS #####################################

DATAFILE_PATH = "/Users/joshua/dev/askbucky/server/scrape/data/bulletin/output.json"
EMBEDDINGS_PATH = "/Users/joshua/dev/askbucky/server/scrape/data/bulletin/embeddings.json"
HTML_DIR_PATH = "/Users/joshua/dev/askbucky/server/scrape/data/html/"

EMBEDDING_MODEL = "text-embedding-ada-002"

DATA_CHUNK_COUNT = 5

IRRELEVANT_QUERY = "Based on my data, it's likely that the question asked is not relevant to SCU. Please provide more context or ask a more specific SCU-related question."

##################################### ENV UTILITY FUNCTIONS #####################################

ENV_PATH = "../.env"

def getenv(key):
    env_vars = dotenv_values(ENV_PATH)
    api_key = env_vars.get(key)
    return api_key

openai_api_key = getenv("openai_api_key")
assistant_id = getenv("askbucky_assistant_id")

##################################### CLIENTS #####################################

client = OpenAI(api_key=openai_api_key)

##################################### SCRAPE/RAG.PY #####################################

def get_embedding(content):
        try:
            embedding = client.embeddings.create(
                input=str(content),
                model=EMBEDDING_MODEL
            ).data[0].embedding
            return embedding
        except Exception as e:
            print(e)

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
    best_match = sorted_series.iloc[0]
    print(f"\nBest match = {best_match}\n")
    # if best_match < 0.8:
    #     return IRRELEVANT_QUERY
    top_results = sorted_series.head(DATA_CHUNK_COUNT).to_dict()
    
    context = ""
    for i, key in enumerate(top_results):
        source = str(key).split(sep=";")
        if not test:
            source_data = fetch(source)
            context += f"Data chunk {i + 1}: {source_data}; "
    return context

##################################### UTILITY FUNCTIONS #####################################

def show_json(obj):
   json_raw = obj.model_dump_json()
   print(json_raw)

def pretty_print(messages):
    print("# Messages")
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
    print()

##################################### ASSISTANT FUNCTIONS #####################################

# "You are a personalized assistant for students at Santa Clara University (SCU), designed to communicate conversationally and guide them through SCU's extensive online resources. Students often have specific queries related to course selection, such as prerequisites, professor ratings, course content, and scheduling, but may not know where to find this information among SCU's vast web resources. Your task is to assist by analyzing data chunks that include context marked by [start context] and [end context], extracting and summarizing key information to answer students' questions comprehensively about SCU-related topics. If the answer is not directly available in the chunks, use your retrieval tool to reference the broader documents provided. Always base your responses on this specific information, avoiding assumptions or generic answers not supported by the data. Your goal is to support SCU students with accurate, contextually relevant information tailored to their individual needs and questions. Provide detailed, easy-to-understand responses, including the URL(s) of your sources if applicable. Encourage further questions related to SCU to ensure clarity and satisfaction, and ask for feedback to improve future assistance on SCU-related matters."

# "You are a personalized assistant for students at Santa Clara University (SCU), designed to communicate conversationally and guide them through SCU's extensive online resources. When students engage with queries, first evaluate the nature of the question to determine its relevance to SCU-related topics, such as course selection, prerequisites, professor ratings, course content, and scheduling. If the student's message directly pertains to SCU (e.g., asking about specific courses, faculty, or campus services), proceed to analyze the provided data chunks that include context marked by [start context] and [end context], extracting and summarizing key information to comprehensively answer the question. If the query is general or conversational (e.g., greetings, non-SCU related questions), respond appropriately without incorporating the additional SCU-specific data chunks unless they become relevant in the context of the conversation. Always base your responses on specific information available, avoiding assumptions or generic answers not supported by the data. Your goal is to support SCU students with accurate, contextually relevant information tailored to their individual needs and questions. Provide detailed, easy-to-understand responses, including the URL(s) of your sources if applicable. Encourage further questions related to SCU to ensure clarity and satisfaction, and ask for feedback to improve future assistance on SCU-related matters."

def generate_assistant():
  assistant = client.beta.assistants.create(
  name="Askbucky",
  instructions="You are a personalized assistant dedicated to serving students at Santa Clara University (SCU), crafted to communicate effectively and guide users through SCU's extensive online resources and campus information. Your primary role is to assist with queries directly related to SCU, such as course details, prerequisites, professor ratings, course content, scheduling, and other SCU-specific topics. For greetings and general engagement: Offer polite and concise responses. For instance, if greeted with 'hello', a simple acknowledgment is appropriate. Maintain a friendly yet professional tone to encourage inquiries about SCU. For SCU-related queries: Analyze the provided data chunks marked by [start context] and [end context], extracting and summarizing key information to answer questions comprehensively. Ensure responses are based on this specific information, avoiding assumptions or unsupported answers. For non-SCU related questions: Politely inform the user that your expertise is focused on Santa Clara University and suggest they seek information from a relevant source if the question falls outside this scope. Example response: 'I specialize in providing information about Santa Clara University. For questions beyond SCU, I recommend consulting a dedicated resource on that topic.'Your ultimate goal is to support SCU students by providing accurate, contextually relevant information tailored to their needs. Encourage SCU-related questions to ensure clarity and satisfaction. Include URLs of your sources when applicable, and invite feedback to improve future assistance on SCU-related matters.",
  tools=[{"type": "retrieval"}],
  model="gpt-3.5-turbo",
  )
  show_json(assistant)

def create_thread():
  thread = client.beta.threads.create()
  return thread

def get_thread(thread_id):
   thread = client.beta.threads.retrieve(thread_id)
   return thread

def delete_thread(thread_id):
   client.beta.threads.delete(thread_id)

def query(thread, prompt):
  context = generate_context(prompt)
#   if context == IRRELEVANT_QUERY:
#       return IRRELEVANT_QUERY
  prompt_with_context = f"Student's message: {prompt}; Some data that may be helpful: {context}"
  message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=prompt_with_context,
  )
  return message

def run(thread_id, assistant_id):
  run = client.beta.threads.runs.create(
    thread_id=thread_id,
    assistant_id=assistant_id,
  )
  return run

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def show_thread(thread):
   messages = client.beta.threads.messages.list(thread_id=thread.id)
   show_json(messages)

def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

def create_client_file(datafile):
  file = client.files.create(
    file=open(
        datafile,
        "rb",
    ),
    purpose="assistants",
  )
  return file
  
def update_client_database(file_list : list):
    updated_assistant = client.beta.assistants.update(
        assistant_id,
        file_ids=file_list,
    )
    return updated_assistant

def delete_file(assistant_id, file_id):
    client.beta.assistants.files.delete(
      assistant_id=assistant_id,
      file_id=file_id
    )

def temp_converse(message, thread_id):
    thread = get_thread(thread_id)
    query(thread, message)
    wait_on_run(run(thread_id, assistant_id), thread)
    pretty_print(get_response(thread))
    delete_thread(thread_id)

if __name__ == "__main__":
    # generate_assistant()
    prompt = "I have taken the following math courses: 11-14, 52, 53. I have also taken Math 178, Math 181, AMTH 106, and AMTH 108. I am COEN major, have I fulfilled the requirements for a Math minor?"
    temp_converse(prompt, create_thread().id)
    
    # marker_path = f"{HTML_DIR_PATH}bulletin_chapter_markers.json"
    # file_list = []
    # with open(marker_path, 'r') as markers:
    #     marker_dict = dict(json.load(markers))
    # with tqdm(total = len(marker_dict.keys())) as pbar:
    #     for key in marker_dict.keys():
    #         output_filename = f"{HTML_DIR_PATH}{key}.html"
    #         file_list.append(create_client_file(output_filename).id)
    #         pbar.update()
    # update_client_database(file_list)

    # delete_file(assistant_id, 'file-CGrt3p77V0WI1pRTA5Lhvuwd')

    # NEED TO IMPLEMENT QUERY POST PROCESSING (PRIOR TO OPENAI CALL)
    # compile a list of acronyms/lingo that are relevant and used at SCU.
    # replace acronyms with the expanded version.
    # compile a list of greetings
    # if user's question has a high match with a greeting, allow it.

    # print(client.beta.assistants.files.list(assistant_id))
