import chromadb
import app.db as my_chroma_db
from scrape.embed import get_embedding

#################### Retrieval Functions ####################

def retrieve_chroma_collection(collection_name='SCU_Undergraduate_Bulletin_2023-2024'):
    collection = my_chroma_db.get_or_create_collection(collection_name)
    return collection

def retrieve_record_by_ID(collection: chromadb.Collection, ids: list):
    record = collection.get(ids=ids)
    return record

def retrieve_context(collection: chromadb.Collection, queries: list, num_results=5):
    collection_size = collection.count()

    query_embedding = get_embedding(queries[0])
    initial_context = collection.query(query_embeddings=query_embedding, n_results=num_results)

    initial_context_ids = initial_context['ids'][0]
    
    def generate_additional_context_ids(doc_id: int, std_deviation: int, min_val: int, max_val: int):
        lower_bound = max(doc_id - std_deviation, min_val)
        upper_bound = min(doc_id + std_deviation, max_val)
        
        generated_list = list(range(lower_bound, upper_bound + 1))
        pruned_list = [value for value in generated_list if min_val <= value <= max_val]
        
        return pruned_list

    sections = {}
    for i, id in enumerate(initial_context_ids):
        section = {}
        id_index = int((id.split('doc'))[1])
        additional_context_ids = generate_additional_context_ids(doc_id=id_index, std_deviation=2, min_val=1, max_val=collection_size)
        for add_ctx_id in additional_context_ids:
            add_ctx_dict = retrieve_record_by_ID(collection=collection, ids=[f'doc{add_ctx_id}'])
            section[f'doc{add_ctx_id}'] = add_ctx_dict
        sections[f'section{i}'] = section
    
    def create_paragraph_from_section(section):
        paragraph = ''
        for key, value in section.items():
            if key.startswith('doc') and value is not None:
                metadatas = value.get('metadatas', [])
                h1 = ''
                h2 = ''
                h3 = ''
                url = ''
                for metadata in metadatas:
                    h1 = metadata.get('h1', '')
                    h2 = metadata.get('h2', '')
                    h3 = metadata.get('h3', '')
                    url = metadata.get('url', '')
                documents = value.get('documents', [])
                paragraph += f'{key}:\n'
                paragraph += f'URL: {url}\n'
                if not h1=='':
                    paragraph += f'h1 header: {h1}\n'
                if not h2=='':
                    paragraph += f'h2 header: {h2}\n'
                if not h3=='':
                    paragraph += f'h3 header: {h3}\n'
                for doc in documents:
                    paragraph += f'Content: {doc}\n'
                paragraph += '\n'
        return paragraph
    
    sections_paragraphs = ''
    for key in sections.keys():
        paragraph = '{}{}{}{}'.format(key, ':\n', create_paragraph_from_section(sections[key]), '\n')
        sections_paragraphs += paragraph

    return sections_paragraphs

def generate_sections(query, num_sections):
    collection = retrieve_chroma_collection()
    queries = [query]
    output = retrieve_context(collection=collection, queries=queries, num_results=num_sections)
    return output

    # take ids of top results. For each id in top results, get the two docs before and two docs after -- this creates a section. For each docID, make a 'message' inclusive of everything associated with that docID, namely the metadata and document itself. Send a message to OpenAI and ask it to return the most relevant section. Once the most relevant section is retrieved, send another request to OpenAI including the user's prompt and most relevant section to get the best response.
    # TODO: Ask someone to create a "Tell me about yourself" window on the Askbucky home screen. Once saved/submitted it will be appended to the system prompt to generate the most user-relevant and accurate responses.