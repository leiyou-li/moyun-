from flask import Flask, request, jsonify
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

@app.route('/')
def home():
    return app.send_static_file('index.html')

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

if __name__ == '__main__':
    # 确保static文件夹存在
    os.makedirs('static', exist_ok=True)
    
    # 将index.html移动到static文件夹
    if os.path.exists('index.html'):
        os.rename('index.html', 'static/index.html')
        
    # 在生产环境中，应该使用正确的WSGI服务器
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 