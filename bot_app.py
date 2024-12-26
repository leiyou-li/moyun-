import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTextEdit, QLineEdit, QPushButton, 
                           QLabel, QMenuBar, QMenu, QDialog, QDialogButtonBox,
                           QFormLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon, QAction
import json
from simple_bot import SimpleBot

class ApiKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API密钥设置")
        self.setModal(True)
        
        layout = QFormLayout(self)
        
        # 创建输入框
        self.openai_key = QLineEdit(self)
        self.serper_key = QLineEdit(self)
        
        # 从配置文件加载已保存的密钥
        try:
            with open('api_keys.json', 'r') as f:
                keys = json.load(f)
                self.openai_key.setText(keys.get('openai', ''))
                self.serper_key.setText(keys.get('serper', ''))
        except:
            pass
            
        # 添加到布局
        layout.addRow("OpenAI API密钥:", self.openai_key)
        layout.addRow("Serper API密钥:", self.serper_key)
        
        # 添加按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_keys(self):
        return {
            'openai': self.openai_key.text(),
            'serper': self.serper_key.text()
        }

class ChatbotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initBot()
        
    def initBot(self):
        self.bot = SimpleBot('智能助手')
        # 尝试加载API密钥
        try:
            with open('api_keys.json', 'r') as f:
                keys = json.load(f)
                self.bot.openai_api_key = keys.get('openai', '')
                self.bot.serper_api_key = keys.get('serper', '')
        except:
            pass
        
    def initUI(self):
        self.setWindowTitle('智能学习机器人')
        self.setGeometry(100, 100, 800, 600)
        
        # 创建主窗口部件和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 创建菜单栏
        menubar = self.menuBar()
        settings_menu = menubar.addMenu('设置')
        
        # 添加API设置菜单项
        api_action = QAction('API密钥设置', self)
        api_action.triggered.connect(self.show_api_dialog)
        settings_menu.addAction(api_action)
        
        # 聊天显示区域
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        layout.addWidget(self.chat_area)
        
        # 输入区域
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.send_message)
        send_button = QPushButton('发送')
        send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_button)
        layout.addLayout(input_layout)
        
        # 状态标签
        self.status_label = QLabel('准备就绪')
        layout.addWidget(self.status_label)
        
        # 显示欢迎消息
        self.display_bot_message('''=== 智能学习机器人已启动 ===
输入 "帮助" 查看我能做什么
''')
        
        # 检查API密钥
        if not self.bot.openai_api_key or not self.bot.serper_api_key:
            self.status_label.setText('提示：请在设置中配置API密���以启用自主学习功能')
            
    def show_api_dialog(self):
        dialog = ApiKeyDialog(self)
        if dialog.exec():
            keys = dialog.get_keys()
            # 保存密钥
            with open('api_keys.json', 'w') as f:
                json.dump(keys, f)
            # 更新机器人的API密钥
            self.bot.openai_api_key = keys['openai']
            self.bot.serper_api_key = keys['serper']
            self.status_label.setText('API密钥已更新')
            
    def display_bot_message(self, message):
        self.chat_area.append(f'机器人: {message}\n')
        
    def display_user_message(self, message):
        self.chat_area.append(f'你: {message}\n')
        
    def send_message(self):
        message = self.input_field.text().strip()
        if not message:
            return
            
        # 清空输入框
        self.input_field.clear()
        
        # 显示用户消息
        self.display_user_message(message)
        
        # 更新状态
        self.status_label.setText('正在思考...')
        
        # 使用定时器来异步处理响应
        QTimer.singleShot(100, lambda: self.process_response(message))
        
    def process_response(self, message):
        try:
            # 获取机器人响应
            response = self.bot.respond(message)
            # 显示响应
            self.display_bot_message(response)
            # 更新状态
            self.status_label.setText('准备就绪')
        except Exception as e:
            self.status_label.setText(f'发生错误: {str(e)}')
            self.display_bot_message('抱歉，我遇到了一点问题，请稍后再试。')

def main():
    app = QApplication(sys.argv)
    window = ChatbotWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 