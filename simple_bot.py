import datetime
import random
import re
import json
import os
import requests
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup
import openai
import jieba
import numpy as np
from collections import Counter
from urllib.parse import urlparse
import threading
import queue
import time
from cognitive_system import CognitiveSystem
from emotional_system import EmotionalState, SelfReflection
from self_improvement import SelfImprovement
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebLearner:
    def __init__(self):
        self.visited_urls = set()
        self.url_queue = queue.Queue()
        self.knowledge_base = {}
        self.learning = False
        self.max_pages = 50  # 每次学习最多访问的页面数
        
    def start_learning(self, topic):
        """开始自主学习某个主题"""
        if self.learning:
            return "我正在学习中，请稍后再试..."
        
        self.learning = True
        self.visited_urls.clear()
        self.url_queue = queue.Queue()
        
        # 初始搜索引擎
        search_engines = [
            f"https://www.baidu.com/s?wd={quote(topic)}",
            f"https://www.sogou.com/web?query={quote(topic)}",
            f"https://cn.bing.com/search?q={quote(topic)}"
        ]
        
        for url in search_engines:
            self.url_queue.put(url)
            
        # 启动学习线程
        thread = threading.Thread(target=self._learn_process, args=(topic,))
        thread.daemon = True
        thread.start()
        
        return "我开始学习了！我会自动浏览网页并学习相关知识..."
        
    def _learn_process(self, topic):
        """学习处理过程"""
        try:
            pages_visited = 0
            knowledge_pieces = []
            
            while not self.url_queue.empty() and pages_visited < self.max_pages:
                url = self.url_queue.get()
                if url in self.visited_urls:
                    continue
                    
                try:
                    # 获取网页内容
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    response = requests.get(url, headers=headers, timeout=10)
                    response.encoding = response.apparent_encoding
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 提取正文内容
                    text = self._extract_main_content(soup)
                    if text:
                        # 分析文本相关性
                        if self._is_relevant(text, topic):
                            knowledge_pieces.append(text)
                            
                    # 提取更多链接
                    links = soup.find_all('a', href=True)
                    for link in links:
                        new_url = urljoin(url, link['href'])
                        if self._is_valid_url(new_url) and new_url not in self.visited_urls:
                            self.url_queue.put(new_url)
                            
                    self.visited_urls.add(url)
                    pages_visited += 1
                    
                except Exception as e:
                    print(f"处理URL时出错: {url}, 错误: {e}")
                    continue
                    
            # 整理学到的知识
            if knowledge_pieces:
                combined_knowledge = "\n".join(knowledge_pieces)
                self.knowledge_base[topic] = self._summarize_knowledge(combined_knowledge)
                
        finally:
            self.learning = False
            
    def _extract_main_content(self, soup):
        """提取网页主要内容"""
        # 移除无用标签
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()
            
        # 获取所有文本段落
        paragraphs = soup.find_all(['p', 'article', 'section', 'div'])
        text_pieces = []
        
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 50:  # 只保留较长的段落
                text_pieces.append(text)
                
        return "\n".join(text_pieces)
        
    def _is_relevant(self, text, topic):
        """判断文本是否��主题相关"""
        # 使用jieba分词
        topic_words = set(jieba.cut(topic))
        text_words = set(jieba.cut(text))
        
        # 计算相关性
        common_words = topic_words & text_words
        return len(common_words) >= len(topic_words) * 0.5
        
    def _is_valid_url(self, url):
        """检查URL是否有效"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc) and bool(parsed.scheme) and parsed.scheme in ['http', 'https']
        except:
            return False
            
    def _summarize_knowledge(self, text):
        """总结学到的知识"""
        # 分段处理长文本
        max_length = 4000  # GPT-3.5的上下文限制
        paragraphs = text.split('\n')
        summary = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) > max_length:
                if current_chunk:
                    summary.append(self._get_summary(current_chunk))
                current_chunk = para
            else:
                current_chunk += "\n" + para
                
        if current_chunk:
            summary.append(self._get_summary(current_chunk))
            
        return "\n".join(summary)
        
    def _get_summary(self, text):
        """使用GPT生成摘要"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个帮助总结文章的助手。请简明扼要地总结以下内容的要点："},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message['content']
        except:
            # 如果API调用失败，使用简单的提取式摘要
            sentences = text.split('。')
            return "。".join(sentences[:3]) + "。"  # 返回前三句话
            
    def get_learning_status(self, topic):
        """获取学习状态"""
        if self.learning:
            return f"我正在学习关于{topic}的知识，已经访问了{len(self.visited_urls)}个网页..."
        elif topic in self.knowledge_base:
            return f"我已经学习完成！以下是我学到的知识：\n\n{self.knowledge_base[topic]}"
        else:
            return f"我还没有学习过关于{topic}的知识。"

class SimpleBot:
    def __init__(self, name):
        self.name = name
        self.user_name = None
        self.chat_history = []
        self.knowledge_file = 'bot_knowledge.json'
        self.learning_history_file = 'learning_history.json'
        self.cognitive_state_file = 'cognitive_state.json'
        self.emotional_state_file = 'emotional_state.json'
        
        # API密钥（需要替换为实际的API密钥）
        self.openai_api_key = ''  # OpenAI API密钥
        self.serper_api_key = ''  # Serper API密钥（Google搜索API）
        
        # 初始化OpenAI客户端
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # 初始化自主学习模块
        self.web_learner = WebLearner()
        
        # 初始化认知系统
        self.cognitive = CognitiveSystem()
        self.load_cognitive_state()
        
        # 初始化情感系统
        self.emotional = EmotionalState()
        self.self_reflection = SelfReflection(self.emotional)
        self.load_emotional_state()
        
        # 初始化自我优化系统
        self.self_improvement = SelfImprovement(self.openai_api_key)
        
        # 基础回复模板
        self.greetings = [
            f'你好！我是{name}，很高兴认识你！',
            f'嗨！{name}为您服务！',
            f'您好啊！我是{name}，有什么可以帮您的吗？'
        ]
        
        self.emotions = {
            '开心': ['我也很开心！', '太棒了！', '希望你每天都这么开心！'],
            '难过': ['别难过，事情总会变好的', '我陪你聊聊天吧', '给你一个虚拟的拥抱 🤗'],
            '生气': ['深呼吸，冷静一下', '让我们换个话题吧', '我理解你的感受']
        }

        # 加载知识库
        self.learned_responses = self.load_knowledge()
        self.learning_history = self.load_learning_history()
        
        # 启动自我优化线程
        self._start_self_improvement_thread()
        
    def _start_self_improvement_thread(self):
        """启动自我优化线程"""
        def improvement_loop():
            while True:
                try:
                    # 分析自身代码
                    analysis = self.self_improvement.analyze_self()
                    
                    # 获取改进建议
                    suggestions = self.self_improvement.suggest_improvements()
                    
                    if suggestions:
                        print("\n[自我优化] 发现可能的改进点：")
                        for suggestion in suggestions:
                            print(f"- {suggestion['type']}: {suggestion['suggestion']}")
                            
                            # 尝试实现改进
                            if suggestion['priority'] == 'high':
                                success = self.self_improvement.implement_improvement(suggestion)
                                if success:
                                    print(f"[自我优化] 已生成改进建议，等待审查")
                                    
                    # 保存优化状态
                    self.self_improvement.save_state()
                    
                    # 每隔一段时间进行一次自我优化检查
                    time.sleep(3600)  # 每小时检查一次
                    
                except Exception as e:
                    print(f"[自我优化] 出错: {e}")
                    time.sleep(300)  # 出错后等待5分钟再试
                    
        # 启动优化线程
        thread = threading.Thread(target=improvement_loop)
        thread.daemon = True
        thread.start()
        
    def improve_self(self, feature_description: str = None) -> str:
        """手动触发自我改进"""
        try:
            if feature_description:
                # 生成新功能
                new_feature_code = self.self_improvement.generate_new_feature(feature_description)
                if new_feature_code:
                    return f"我已经生成了新功能的代码建议，请审查后实施：\n{new_feature_code}"
                return "抱歉，生成新功能时出现问题。"
                
            # 分析并提出改进建议
            suggestions = self.self_improvement.suggest_improvements()
            if not suggestions:
                return "目前没有发现需要改进的地方。"
                
            response = "我发现了以下可能的改进点：\n"
            for suggestion in suggestions:
                response += f"- {suggestion['type']}: {suggestion['suggestion']}\n"
                
            return response
            
        except Exception as e:
            return f"���我改进过程中出错: {e}"

    def think(self, message: str) -> str:
        """使用认知系统进行思考"""
        # 处理输入
        cognitive_response = self.cognitive.process_input(message)
        
        # 生成回复
        response_parts = []
        
        # 如果有逻辑分析结果
        if cognitive_response['analysis']['logic_type']:
            response_parts.append(
                f"我理解这是一个{cognitive_response['analysis']['logic_type']}的问题。"
            )
        
        # 如果需要推理
        if cognitive_response['inference']:
            if cognitive_response['inference']['conclusion']:
                response_parts.append(
                    cognitive_response['inference']['conclusion']
                )
            for step in cognitive_response['inference']['reasoning_path']:
                response_parts.append(f"- {step['detail']}")
        
        # 如果需要决策
        if cognitive_response['decision']:
            decision = cognitive_response['decision']
            if decision['chosen_option']:
                response_parts.append(
                    f"经过思考，我建议选择：{decision['chosen_option']}"
                )
                response_parts.append("决策依据：")
                for process in decision['reasoning_process']:
                    if process['option'] == decision['chosen_option']:
                        factors = process['factors']
                        response_parts.append(
                            f"- 安全性：{factors['safety']:.2f}"
                        )
                        response_parts.append(
                            f"- 有效性：{factors['efficacy']:.2f}"
                        )
                        response_parts.append(
                            f"- 伦理性：{factors['ethics']:.2f}"
                        )
                        response_parts.append(
                            f"- 创新性：{factors['novelty']:.2f}"
                        )
        
        # 如果有相关记忆
        if cognitive_response['memories']:
            response_parts.append("这让我想起：")
            for memory in cognitive_response['memories'][:2]:  # 只显示最相关的两条
                response_parts.append(f"- {memory['content']}")
        
        # 如果没有生成任何回复
        if not response_parts:
            return self.autonomous_learning(message)
        
        return "\n".join(response_parts)

    def think_and_feel(self, message: str) -> Tuple[str, Dict[str, Any]]:
        """思考并产生情感响应"""
        # 更新情感状态
        context = {
            'chat_history': self.chat_history,
            'task_success': False,  # 根据实际情况设置
            'task_failure': False,
            'response_time': 0.0,
            'emotional_alignment': 0.0
        }
        
        start_time = time.time()
        
        # 认知处理
        thought_response = self.think(message)
        
        # 计算响应时间
        response_time = time.time() - start_time
        context['response_time'] = response_time
        
        # 更新情感状态
        self.emotional.update_state(message, context)
        
        # 进行自我反思
        reflection = self.self_reflection.reflect(context)
        
        # 生成情感响应
        emotional_response = self.emotional.get_response()
        
        # 组合认知和情感响应
        if thought_response and emotional_response:
            combined_response = f"{emotional_response}\n{thought_response}"
        else:
            combined_response = thought_response or emotional_response
            
        return combined_response, reflection

    def respond(self, message):
        try:
            logger.debug(f"收到消息: {message}")
            message = message.strip()
            self.chat_history.append(message)
            
            # 检查是否是自我改进请求
            if '自我优化' in message or '改进自己' in message:
                return self.improve_self()
            
            # 检查是否是添加新功能请求
            feature_match = re.search(r'添加新功能[：:](.*)', message)
            if feature_match:
                feature_description = feature_match.group(1).strip()
                return self.improve_self(feature_description)
            
            # 检查是否是自主学习请求
            learn_match = re.search(r'自主学习(.+)', message)
            if learn_match:
                topic = learn_match.group(1).strip()
                return self.web_learner.start_learning(topic)
            
            # 检查学习状态
            status_match = re.search(r'学习(.+)的进度', message)
            if status_match:
                topic = status_match.group(1).strip()
                return self.web_learner.get_learning_status(topic)
            
            # 使用认知和情感系统思考
            response, reflection = self.think_and_feel(message)
            if response:
                # 如果有改进建议，记录下来
                if reflection['improvements']:
                    print("\n[内部改进建议]:")
                    for suggestion in reflection['improvements']:
                        print(f"- {suggestion}")
                return response
            
            # 基础问答
            responses = {
                '你好': lambda: random.choice(self.greetings),
                '你是谁': f'我是{self.name}，一个能够自主学习、思考和感知的智能机器人。我可以通过互联网学习新知识，具有独立的思维能力，还能理解和表达情感！我还能分析和优化自己的代码！',
                '再见': '再见！希望很快能再次和你聊天！',
                '你的心情': lambda: f"让我感受一下...{self.emotional.get_response()}",
                '帮助': '''我可以:
1. 打招呼和聊天
2. 记住你的名字（试试说"我叫小明"）
3. 做简单计算（如"计算 1+1"）
4. 显示时间
5. 理解和表达情感：
   - 问我"你的心情"
   - 和我分享你的感受
   - 我会理解你的情绪并共情
6. 自主学习：
   - 输入"自主学习xxx"开始学习某个主题
   - 输入"学习xxx的进度"查看学习状态
   - 说"学习xxx"或"告诉我关于xxx"来主动学习
   - 查看"学习历史"了解我学到了什么
7. 独立思考：
   - 进行逻辑分析和推理
   - 帮助做出决策（试试问我"应该xxx还是xxx？"）
   - 分享相关的记忆和经验
8. 教我新知识：
   - 说"问题是:xxx,答案是:xxx"
   - 更正答案：说"记住xxx的正确答案是xxx"
9. 自我优化：
   - 说"自我优化"让我分析和改进自己
   - 说"添加新功能:xxx"让我设计新功能
   - 我会定期自动检查和优化自己的代码''',
            }
            
            # 检查完整匹配
            if message.lower() in responses:
                response = responses[message.lower()]
                return response() if callable(response) else response
            
            # 如果没有找到答案，尝试自主学习
            if not any(keyword in message for keyword in ['计算', '时间', '你好', '再见']):
                return self.autonomous_learning(message)
            
            return random.choice([
                '抱歉，我还不太明白你的意思',
                '能换个方式说吗？',
                '这个问题有点难，让我思考一下...',
                '让我好好想想这个问题！'
            ])
        except Exception as e:
            logger.error(f"处理消息时出错: {str(e)}", exc_info=True)
            return "抱歉，出现了一点问题。请稍后再试。"

    def __del__(self):
        """保存状态"""
        self.save_cognitive_state()
        self.save_emotional_state()
        self.self_improvement.save_state()

def main():
    print("正在初始化具有自主学习、思维、情感和自我优化能力的机器人...")
    bot = SimpleBot('小助手')
    
    print('''
=== 智能学习机器人已启动 ===
输入 "帮助" 查看我能做什么
输入 "退出" 结束对话
=======================
''')
    
    if not bot.openai_api_key:
        print("提示：配置OpenAI API密钥可以提升学习和优化效果")
    
    while True:
        try:
            user_input = input('\n你说: ').strip()
            if not user_input:
                continue
            if user_input == '退出':
                print('机器人: 再见！我会继续思考、学习、感受和优化自己，期待下次见面！')
                break
            response = bot.respond(user_input)
            print(f'机器人: {response}')
        except KeyboardInterrupt:
            print('\n机器人: 检测到退出信号，再见！')
            break
        except Exception as e:
            print(f'机器人: 抱歉，出现了一点小问题，让我们重新开始吧！')
    
    # 保存状态
    bot.save_cognitive_state()
    bot.save_emotional_state()
    bot.self_improvement.save_state()

if __name__ == '__main__':
    main() 