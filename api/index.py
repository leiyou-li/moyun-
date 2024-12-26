from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from simple_bot import SimpleBot
import os
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)  # 启用跨域请求

# 加载环境变量
load_dotenv()

# 创建机器人实例
bot = SimpleBot('小助手')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(f"static/{path}"):
        return send_from_directory('static', path)
    return send_from_directory('static', 'index.html')

@app.route('/api/bot', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message')
        
        # 获取API密钥
        openai_key = request.headers.get('X-OpenAI-Key')
        serper_key = request.headers.get('X-Serper-Key')
        
        # 如果提供了API密钥，更新机器人的配置
        if openai_key:
            bot.openai_api_key = openai_key
        if serper_key:
            bot.serper_api_key = serper_key
            
        # 获取机器人响应
        response = bot.respond(message)
        
        return jsonify({
            'status': 'success',
            'response': response
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Vercel 需要这个处理函数
def handler(request, context):
    with app.request_context(request):
        return app.handle_request() 