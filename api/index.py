from flask import Flask, request, jsonify
from simple_bot import SimpleBot

app = Flask(__name__)
bot = SimpleBot('小助手')

@app.route('/', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        response = bot.respond(message)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run() 