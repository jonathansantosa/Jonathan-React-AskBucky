# main.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from . import context_window
# from . import respond

app = Flask(__name__)
CORS(app, supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*")

chat_history = []

@app.route('/main', methods=['POST'])
def process_input():
    data = request.get_json()
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    socketio.emit('message', {'type': 'user', 'text': user_message})
    
    generator = context_window.generate_response(user_message, chat_history)
    response = ""
    for response_token in generator:
        response += response_token
        socketio.emit('message', {'type': 'bot', 'text': response_token})
    
    # return jsonify({'status': 'succeeded'})

    return response

#Jonathan did something
def run():
    socketio.run(app, 
                debug=True,
                host="0.0.0.0",
                allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    run()
