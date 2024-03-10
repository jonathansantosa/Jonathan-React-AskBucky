import sql_db.simplethread as simplethread
import json
import openai
import os

openai.api_key = os.environ.get("openai_api_key")

MODEL = "gpt-3.5-turbo" # (4096 TCW) will replace with "gpt-3.5-turbo-1106" (16,385 TCW)
MAX_TOKEN_COUNT = 4097
RESPONSE_BUFFER = 1024
TEMPERATURE = 0

def generate_response(prompt, chat_history):

    try:
        messages_for_api = [{'role': 'assistant' if msg['role'] == 'bot' else 'user', 'content': msg['text']} for msg in chat_history]
        messages_for_api.append({'role': 'user', 'content': prompt})
        chat_history.append({'role': 'user', 'text': prompt})

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

        simplethread.appendto_chatThread(1, json.dumps(
                    {'user_prompt': prompt,'assistant_response': response}, indent=4))
        chat_history.append({'role': 'assistant', 'text': response})
    except Exception as e:
        yield f"Sorry, an error occurred while generating a response. {str(e)}"