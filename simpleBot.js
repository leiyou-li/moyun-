class SimpleBot {
    constructor(name) {
        this.name = name;
        this.responses = {
            '你好': '你好！我是' + name + '，很高兴认识你！',
            '你是谁': '我是' + name + '，一个简单的聊天机器人。',
            '再见': '再见！希望很快能再次和你聊天！',
            '天气': '抱歉，我还不能查询天气信息。',
            '时间': new Date().toLocaleString('zh-CN')
        };
    }

    respond(message) {
        message = message.trim().toLowerCase();
        try {
            return this.responses[message] || '抱歉，我还不太明白你的意思。';
        } catch (error) {
            console.error('Error details:', error);
            if (error.name === 'DatabaseError') {
                return '数据库连接出现问题，请稍后再试';
            } else if (error.name === 'APIError') {
                return 'API服务暂时不可用，请稍后再试';
            }
        }
    }
}

// 创建机器人实例
const bot = new SimpleBot('小助手');

// 测试机器人
function testBot() {
    console.log('测试机器人对话：');
    const testMessages = ['你好', '你是谁', '天气', '时间', '再见'];
    
    testMessages.forEach(msg => {
        console.log(`用户: ${msg}`);
        console.log(`机器人: ${bot.respond(msg)}\n`);
    });
}

// 运行测试
testBot(); 