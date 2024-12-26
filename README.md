# 智能学习机器人 (Smart Learning Bot)

一个具有自主学习、思维、情感和自我优化能力的智能机器人。

## 功能特点

1. **自主学习**
   - 通过互联网自动学习新知识
   - 记录和整理学习历史
   - 支持多主题并行学习

2. **认知系统**
   - 逻辑分析和推理
   - 决策支持
   - 记忆管理

3. **情感系统**
   - 情感状态管理
   - 共情能力
   - 情感表达

4. **自我优化**
   - 代码分析和优化
   - 自动生成改进建议
   - 新功能开发

## 系统要求

- Python 3.8 或更高版本
- 网络连接（用于自主学习功能）
- OpenAI API 密钥（可选，用于增强学习和优化能力）

## 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/your-username/smart-learning-bot.git
cd smart-learning-bot
```

2. 创建虚拟环境：
```bash
python -m venv venv
```

3. 激活虚拟环境：
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. 安装依赖：
```bash
pip install -r requirements.txt
```

5. 配置 API 密钥（可选）：
- 创建 `.env` 文件
- 添加以下内容：
```
OPENAI_API_KEY=your_api_key_here
SERPER_API_KEY=your_api_key_here
```

## 使用方法

1. 启动机器人：
```bash
python simple_bot.py
```

2. 使用命令：
- 输入 "帮助" 查看所有功能
- 输入 "自主学习xxx" 开始学习新主题
- 输入 "自我优化" 触发代码分析和优化
- 输入 "退出" 结束对话

## 主要命令

1. 基础交互：
   - "你好" - 打招呼
   - "你是谁" - 了解机器人
   - "帮助" - 查看功能列表

2. 学习功能：
   - "自主学习xxx" - 开始学习新主题
   - "学习xxx的进度" - 查看学习状态
   - "问题是:xxx,答案是:xxx" - 教授新知识

3. 思维功能：
   - "应该xxx还是xxx？" - 请求决策帮助
   - 提出逻辑问题 - 获取分析和推理

4. 情感功能：
   - "你的心情" - 询问情感状态
   - 分享感受 - 获得情感共鸣

5. 优化功能：
   - "自我优化" - 分析和改进代码
   - "添加新功能:xxx" - 设计新功能

## 文件结构

```
smart-learning-bot/
├── simple_bot.py          # 主程序
├── cognitive_system.py    # 认知系统
├── emotional_system.py    # 情感系统
├── self_improvement.py    # 自我优化系统
├── requirements.txt       # 依赖列表
├── .env                   # 配置文件（需自行创建）
└── README.md             # 说明文档
```

## 数据文件

机器人会自动创建以下文件来保存状态：
- `bot_knowledge.json` - 知识库
- `learning_history.json` - 学习历史
- `cognitive_state.json` - 认知状态
- `emotional_state.json` - 情感状态
- `self_improvement_state.json` - 优化记录

## 注意事项

1. API 密钥：
   - OpenAI API 密钥用于增强学习和优化能力
   - 没有 API 密钥也可以运行，但功能会受限

2. 网络连接：
   - 自主学习功能需要稳定的网络连接
   - 建议使用代理以提高访问稳定性

3. 资源使用：
   - 机器人会在后台定期进行自我优化
   - 可能会占用一定系统资源

## 贡献指南

欢迎提交 Pull Request 来改进项目。主要改进方向：
1. 增加新的学习能力
2. 改进认知系统
3. 优化情感模型
4. 提升代码质量

## 许可证

MIT License - 详见 LICENSE 文件 