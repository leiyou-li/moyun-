import numpy as np
from typing import Dict, List, Any, Tuple
import datetime
import json
from collections import defaultdict

class EmotionalState:
    def __init__(self):
        # 基础情感维度
        self.dimensions = {
            'pleasure': 0.0,     # 愉悦度 (-1 到 1)
            'arousal': 0.0,      # 激活度 (-1 到 1)
            'dominance': 0.0,    # 控制度 (-1 到 1)
        }
        
        # 情感记忆
        self.emotional_memory = []
        self.max_memory = 100
        
        # 情感词典
        self.emotion_dict = {
            '开心': {'pleasure': 0.8, 'arousal': 0.5, 'dominance': 0.6},
            '难过': {'pleasure': -0.7, 'arousal': -0.3, 'dominance': -0.4},
            '生气': {'pleasure': -0.6, 'arousal': 0.8, 'dominance': 0.7},
            '害怕': {'pleasure': -0.7, 'arousal': 0.7, 'dominance': -0.8},
            '惊讶': {'pleasure': 0.2, 'arousal': 0.8, 'dominance': 0.0},
            '平静': {'pleasure': 0.3, 'arousal': -0.4, 'dominance': 0.2},
        }
        
        # 情感响应模板
        self.response_templates = defaultdict(list)
        self._init_response_templates()
        
    def _init_response_templates(self):
        """初始化情感响应模板"""
        self.response_templates.update({
            'high_pleasure': [
                '我现在感觉很愉快！',
                '这真是太棒了！',
                '我很高兴能和你交流！'
            ],
            'low_pleasure': [
                '这确实让人有点难过...',
                '我能理解这种感受',
                '让我们一起面对这个问题'
            ],
            'high_arousal': [
                '这太令人兴奋了！',
                '我现在充满干劲！',
                '让我们积极行动起来！'
            ],
            'low_arousal': [
                '我们需要冷静下来想想',
                '让我们慢慢来',
                '保持平和的心态很重要'
            ]
        })
        
    def update_state(self, input_text: str, context: Dict[str, Any]) -> None:
        """更新情感状态"""
        # 分析输入文本的情感倾向
        emotion_scores = self._analyze_emotion(input_text)
        
        # 考虑上下文影响
        context_impact = self._evaluate_context(context)
        
        # 更新情感维度
        for dimension in self.dimensions:
            # 结合文本情��和上下文影响
            new_value = (emotion_scores.get(dimension, 0) * 0.7 + 
                        context_impact.get(dimension, 0) * 0.3)
            
            # 使用动态衰减
            decay = 0.8
            self.dimensions[dimension] = (
                self.dimensions[dimension] * decay + new_value * (1 - decay)
            )
            
            # 确保值在[-1, 1]范围内
            self.dimensions[dimension] = max(-1, min(1, self.dimensions[dimension]))
            
        # 记录情感状态
        self._record_emotional_state(input_text)
        
    def _analyze_emotion(self, text: str) -> Dict[str, float]:
        """分析文本的情感倾向"""
        scores = {
            'pleasure': 0,
            'arousal': 0,
            'dominance': 0
        }
        
        # 检查情感词
        for emotion, values in self.emotion_dict.items():
            if emotion in text:
                for dimension, value in values.items():
                    scores[dimension] += value
                    
        # 归一化分数
        max_abs = max(abs(v) for v in scores.values()) or 1
        return {k: v/max_abs for k, v in scores.items()}
        
    def _evaluate_context(self, context: Dict[str, Any]) -> Dict[str, float]:
        """评估上下文对情感的影响"""
        impact = {
            'pleasure': 0,
            'arousal': 0,
            'dominance': 0
        }
        
        # 分析对话历史
        if 'chat_history' in context:
            recent_messages = context['chat_history'][-3:]  # 只看最近3条
            for msg in recent_messages:
                msg_emotion = self._analyze_emotion(msg)
                for dimension, value in msg_emotion.items():
                    impact[dimension] += value * 0.2  # 历史消息影响较小
                    
        # 分析任务成功/失败
        if context.get('task_success'):
            impact['pleasure'] += 0.3
            impact['dominance'] += 0.2
        elif context.get('task_failure'):
            impact['pleasure'] -= 0.2
            impact['dominance'] -= 0.1
            
        return impact
        
    def _record_emotional_state(self, trigger: str) -> None:
        """记录情感状态"""
        state = {
            'timestamp': datetime.datetime.now().isoformat(),
            'dimensions': self.dimensions.copy(),
            'trigger': trigger
        }
        
        self.emotional_memory.append(state)
        
        # 限制记忆大小
        if len(self.emotional_memory) > self.max_memory:
            self.emotional_memory = self.emotional_memory[-self.max_memory:]
            
    def get_response(self) -> str:
        """根据当前情感状态生成响应"""
        # 确定主导情感维度
        dominant_dimension = max(
            self.dimensions.items(),
            key=lambda x: abs(x[1])
        )
        
        # 选择响应模板
        if dominant_dimension[0] == 'pleasure':
            if dominant_dimension[1] > 0:
                templates = self.response_templates['high_pleasure']
            else:
                templates = self.response_templates['low_pleasure']
        else:  # arousal
            if dominant_dimension[1] > 0:
                templates = self.response_templates['high_arousal']
            else:
                templates = self.response_templates['low_arousal']
                
        return np.random.choice(templates)
        
    def get_emotional_state(self) -> Dict[str, float]:
        """获取当前情感状态"""
        return self.dimensions.copy()
        
    def get_emotional_trend(self, window: int = 10) -> Dict[str, List[float]]:
        """分析情感趋势"""
        if not self.emotional_memory:
            return {dim: [] for dim in self.dimensions}
            
        recent_states = self.emotional_memory[-window:]
        trends = {dim: [] for dim in self.dimensions}
        
        for state in recent_states:
            for dim, value in state['dimensions'].items():
                trends[dim].append(value)
                
        return trends

class SelfReflection:
    def __init__(self, emotional_state: EmotionalState):
        self.emotional_state = emotional_state
        self.reflection_log = []
        self.learning_points = defaultdict(list)
        self.improvement_suggestions = defaultdict(list)
        
    def reflect(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """进行自我反思"""
        reflection = {
            'timestamp': datetime.datetime.now().isoformat(),
            'emotional_state': self.emotional_state.get_emotional_state(),
            'analysis': {},
            'learnings': [],
            'improvements': []
        }
        
        # 分析情感变化
        emotional_trend = self.emotional_state.get_emotional_trend()
        reflection['analysis']['emotional_trend'] = self._analyze_emotional_trend(
            emotional_trend
        )
        
        # 分析交互质量
        interaction_quality = self._analyze_interaction_quality(interaction_data)
        reflection['analysis']['interaction_quality'] = interaction_quality
        
        # 总结学习点
        learnings = self._extract_learning_points(interaction_data)
        reflection['learnings'] = learnings
        
        # 生成改进建议
        improvements = self._generate_improvements(
            interaction_quality, learnings
        )
        reflection['improvements'] = improvements
        
        # 记录反思结果
        self.reflection_log.append(reflection)
        
        return reflection
        
    def _analyze_emotional_trend(self, trend: Dict[str, List[float]]) -> Dict[str, Any]:
        """分析情感趋势"""
        analysis = {}
        
        for dimension, values in trend.items():
            if not values:
                continue
                
            # 计算变化率
            changes = np.diff(values)
            
            analysis[dimension] = {
                'direction': 'up' if np.mean(changes) > 0 else 'down',
                'volatility': np.std(changes),
                'average': np.mean(values)
            }
            
        return analysis
        
    def _analyze_interaction_quality(self, data: Dict[str, Any]) -> Dict[str, float]:
        """分析交互质量"""
        quality = {
            'responsiveness': 0.0,  # 响应性
            'empathy': 0.0,        # 共情能力
            'helpfulness': 0.0,    # 帮助程度
            'coherence': 0.0       # 对话连贯性
        }
        
        # 评估响应性
        if 'response_time' in data:
            quality['responsiveness'] = 1.0 - min(1.0, data['response_time'] / 5.0)
            
        # 评估共情能力
        if 'emotional_alignment' in data:
            quality['empathy'] = data['emotional_alignment']
            
        # 评估帮助程度
        if 'user_feedback' in data:
            quality['helpfulness'] = data['user_feedback']
            
        # 评估对话连贯性
        if 'chat_history' in data:
            quality['coherence'] = self._evaluate_coherence(data['chat_history'])
            
        return quality
        
    def _evaluate_coherence(self, chat_history: List[str]) -> float:
        """评估对话连贯性"""
        if len(chat_history) < 2:
            return 1.0
            
        coherence_scores = []
        for i in range(1, len(chat_history)):
            prev = chat_history[i-1]
            curr = chat_history[i]
            
            # 简单的文本相似度计算
            words1 = set(prev.split())
            words2 = set(curr.split())
            similarity = len(words1 & words2) / len(words1 | words2) if words1 | words2 else 0
            
            coherence_scores.append(similarity)
            
        return sum(coherence_scores) / len(coherence_scores)
        
    def _extract_learning_points(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取学习点"""
        learnings = []
        
        # 分析用户反馈
        if 'user_feedback' in data and data['user_feedback'] < 0.6:
            learnings.append({
                'type': 'feedback',
                'point': '需要改进用户满意度',
                'context': data.get('chat_history', [])[-1]
            })
            
        # 分析情感适配度
        if 'emotional_alignment' in data and data['emotional_alignment'] < 0.7:
            learnings.append({
                'type': 'emotion',
                'point': '需要提高情感共鸣能力',
                'context': str(self.emotional_state.get_emotional_state())
            })
            
        # 记录学习点
        for learning in learnings:
            self.learning_points[learning['type']].append(learning)
            
        return learnings
        
    def _generate_improvements(self, quality: Dict[str, float], 
                             learnings: List[Dict[str, Any]]) -> List[str]:
        """生成改进建议"""
        improvements = []
        
        # 基于交互质量生成建议
        for aspect, score in quality.items():
            if score < 0.6:
                suggestion = self._get_improvement_suggestion(aspect)
                improvements.append(suggestion)
                self.improvement_suggestions[aspect].append(suggestion)
                
        # 基于学习点生成建议
        for learning in learnings:
            suggestion = self._get_improvement_suggestion(
                learning['type'], learning['context']
            )
            improvements.append(suggestion)
            self.improvement_suggestions[learning['type']].append(suggestion)
            
        return improvements
        
    def _get_improvement_suggestion(self, aspect: str, context: str = '') -> str:
        """获取改进建议"""
        suggestions = {
            'responsiveness': '提高响应速度，保持对话流畅性',
            'empathy': '增强情感理解和共鸣能力',
            'helpfulness': '提供更具体和实用的帮助',
            'coherence': '保持对话主题的连贯性',
            'feedback': f'根据用户反馈改进：{context}',
            'emotion': f'提高情感适配度：{context}'
        }
        
        return suggestions.get(aspect, '持续改进和学习') 