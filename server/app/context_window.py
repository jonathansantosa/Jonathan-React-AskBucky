import openai
import os
import tiktoken
from datetime import datetime
# import db.simplethread as simplethread
from app.converse import openai_pass_prompt

#################### Globals ####################
MODEL = "gpt-3.5-turbo"
MAX_TOKEN_COUNT = 4097 # API Limit (fixed)
RESPONSE_BUFFER = 1024
TEMPERATURE = 0.5

chat_history_token_count = 0
total_token_count = 0

openai.api_key = os.environ.get("openai_api_key")
tokenizer = tiktoken.encoding_for_model(MODEL)

current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d %H-%M-%S")
file_name = f"logger_{formatted_datetime}.txt"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE_PATH = os.path.join(LOGS_DIR, file_name)

if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

#################### Utility Functions ####################

def calculate_tokens(text):
    return len(list(tokenizer.encode(text)))

#################### Processing Functions ####################

def pre_process(prompt_token_count, chat_history):
    global chat_history_token_count, total_token_count    

    if (len(chat_history) == 0):
        chat_history_token_count = 0 

    with open(LOG_FILE_PATH, 'a') as log_file:
        log_file.write(f"########## Start of Query ##########\n")
        log_file.write(f"Chat history length: {len(chat_history)}\n")
        log_file.write(f"prompt token count: {prompt_token_count}\n")
        log_file.write(f"Check 1: prompt_token_count ({prompt_token_count}) >= MAX_TOKEN_COUNT ({MAX_TOKEN_COUNT})? {prompt_token_count >= MAX_TOKEN_COUNT}\n")
    
    if (prompt_token_count >= MAX_TOKEN_COUNT):
        with open(LOG_FILE_PATH, 'a') as log_file:
            log_file.write(f"Returned Error: The message you sent was too long, please reload the conversation and submit something shorter.\n")
            log_file.write(f"########## Abrupt End of Query ##########\n\n")
        return "The message you sent was too long, please submit something shorter."

    total_token_count = prompt_token_count + chat_history_token_count
    with open(LOG_FILE_PATH, 'a') as log_file:
        log_file.write(f"chat history token count: {chat_history_token_count}\n")
        log_file.write(f"total token count: {total_token_count}\n")
        log_file.write(f"Check 2: total_token_count ({total_token_count}) >= MAX_TOKEN_COUNT ({MAX_TOKEN_COUNT})? {total_token_count >= MAX_TOKEN_COUNT}\n")
        log_file.write(f"Check 3: total_token_count ({total_token_count}) + RESPONSE_BUFFER ({RESPONSE_BUFFER}) >= MAX_TOKEN_COUNT ({MAX_TOKEN_COUNT})? Sum = {total_token_count + RESPONSE_BUFFER} >= MAX_TOKEN_COUNT ({MAX_TOKEN_COUNT})? {total_token_count + RESPONSE_BUFFER >= MAX_TOKEN_COUNT}\n")
    if (total_token_count >= MAX_TOKEN_COUNT):
        apply_fixed_sliding_window(chat_history, prompt_token_count)

    if (total_token_count + RESPONSE_BUFFER >= MAX_TOKEN_COUNT):
        # what happens when initial prompt is 3500? can either request shorter message or shorten response buffer
        # --> convert final to regular var and update the length soley for this particular request.
        # can implement context switching on methods later on 
        if (prompt_token_count + RESPONSE_BUFFER >= MAX_TOKEN_COUNT):
            with open(LOG_FILE_PATH, 'a') as log_file:
                log_file.write(f"Returned Error: The message you sent was too long, please reload the conversation and submit something shorter.\n")
                log_file.write(f"########## Abrupt End of Query ##########\n\n")
            return "The message you sent was too long, please submit something shorter."
        else:
            apply_fixed_sliding_window(chat_history, prompt_token_count)

    return None

def post_process(prompt_token_count, response_token_count):
    global chat_history_token_count, total_token_count

    assert(response_token_count <= MAX_TOKEN_COUNT)
    assert(response_token_count <= RESPONSE_BUFFER)
    assert(total_token_count + response_token_count < MAX_TOKEN_COUNT)

    chat_history_token_count += prompt_token_count + response_token_count
    total_token_count += response_token_count

    with open(LOG_FILE_PATH, 'a') as log_file:
        log_file.write(f"End of post_process: response token count = {response_token_count}, chat history token count = {chat_history_token_count}, total token count = {total_token_count}\n")
        log_file.write(f"########## End of Query ##########\n\n")

#################### Context Window Adjustment Functions ####################

def apply_fixed_sliding_window(chat_history, prompt_token_count):
    global chat_history_token_count, total_token_count

    with open(LOG_FILE_PATH, 'a') as log_file:
        log_file.write(f"Applying Sliding Window: {total_token_count}\n")
        log_file.write(f"total token count ({total_token_count}) > max token count ({MAX_TOKEN_COUNT}) - response buffer ({RESPONSE_BUFFER})? --> ({total_token_count}) > ({MAX_TOKEN_COUNT - RESPONSE_BUFFER})?\n")

    while total_token_count > (MAX_TOKEN_COUNT - RESPONSE_BUFFER):
        with open(LOG_FILE_PATH, 'a') as log_file:
            log_file.write(f"Updated chat history length: {len(chat_history)}\n")
        
        if (len(chat_history) > 0):
            removed_message = chat_history.pop(0)
            removed_message_token_count = calculate_tokens(removed_message['text'])
        else:
            return "Failed to apply sliding window..."
        
        with open(LOG_FILE_PATH, 'a') as log_file:
            log_file.write(f"Removed message: {removed_message}\n")
            log_file.write(f"Removed message token count: {removed_message_token_count}\n")
        
        chat_history_token_count -= removed_message_token_count
        with open(LOG_FILE_PATH, 'a') as log_file:
            log_file.write(f"Updated chat history token count: {chat_history_token_count}\n")
        
        total_token_count = chat_history_token_count + prompt_token_count
        with open(LOG_FILE_PATH, 'a') as log_file:
            log_file.write(f"Updated total token count: {total_token_count}\n")

#################### Response Generation ####################

def generate_response(prompt, chat_history):

    try:
        prompt_token_count = calculate_tokens(prompt) + 4
        pre_process_error = pre_process(prompt_token_count, chat_history)
        if pre_process_error:
            yield pre_process_error
        else:
            messages_for_api = [{'role': 'assistant' if msg['role'] == 'bot' else 'user', 'content': msg['text']} for msg in chat_history]
            request = openai_pass_prompt(prompt)
            for item in request:
                messages_for_api.append(item)

            completion = openai.chat.completions.create(
                model=MODEL, 
                max_tokens=RESPONSE_BUFFER,
                temperature=TEMPERATURE,
                messages=messages_for_api,
                stream=True
            )
            
            response = ""
            for message in completion:
                if message.choices[0].finish_reason is None:
                    content = message.choices[0].delta.content
                    response += content
                    yield content
            
            chat_history.append({'role': 'assistant', 'text': response})
            response_token_count = calculate_tokens(response) + 1
            post_process(prompt_token_count, response_token_count)

    except Exception as e:
        yield f"Sorry, an error occurred while generating a response. {str(e)}"

