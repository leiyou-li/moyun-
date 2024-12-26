import json
import datetime
import re
from collections import defaultdict
import numpy as np
from typing import List, Dict, Any

class Memory:
    def __init__(self):
        self.short_term = []  # 短期记忆
        self.long_term = defaultdict(list)  # 长期记忆
        self.associations = defaultdict(set)  # 概念关联
        self.max_short_term = 10  # 短期记忆容量
        
    def add_memory(self, content: str, category: str = None):
        """添加新记忆"""
        # 添加到短期记忆
        memory_item = {
            'content': content,
            'timestamp': datetime.datetime.now().isoformat(),
            'category': category,
            'importance': self._evaluate_importance(content)
        }
        
        self.short_term.append(memory_item)
        
        # 如果短期记忆满了，进行记忆整合
        if len(self.short_term) > self.max_short_term:
            self._consolidate_memories()
            
    def _evaluate_importance(self, content: str) -> float:
        """评估记忆的重要性"""
        importance = 0.5  # 基础重要性
        
        # 根据关键词调整重要性
        important_keywords = ['重要', '必须', '记住', '关键', '核心']
        for keyword in important_keywords:
            if keyword in content:
                importance += 0.1
                
        # 根据情感词调整重要性
        emotion_keywords = ['开心', '难过', '生气', '惊讶', '害怕']
        for keyword in emotion_keywords:
            if keyword in content:
                importance += 0.1
                
        return min(importance, 1.0)
        
    def _consolidate_memories(self):
        """整合记忆：将短期记忆转化为长期记忆"""
        for memory in self.short_term:
            if memory['importance'] > 0.6:  # 重要的记忆转入长期记忆
                category = memory['category'] or '通用'
                self.long_term[category].append(memory)
                
                # 建立概念关联
                words = set(memory['content'].split())
                for word in words:
                    self.associations[word].update(words - {word})
                
        # 清空短期记忆
        self.short_term = []
        
    def recall(self, query: str, category: str = None) -> List[Dict[str, Any]]:
        """根据查询召回相关记忆"""
        query_words = set(query.split())
        relevant_memories = []
        
        # 搜索长期记忆
        memories_to_search = self.long_term[category] if category else [
            m for memories in self.long_term.values() for m in memories
        ]
        
        for memory in memories_to_search:
            memory_words = set(memory['content'].split())
            # 计算相关性
            relevance = len(query_words & memory_words) / len(query_words)
            if relevance > 0.3:  # 相关性阈值
                relevant_memories.append({
                    'content': memory['content'],
                    'relevance': relevance,
                    'timestamp': memory['timestamp']
                })
                
        # 按相关性排序
        return sorted(relevant_memories, key=lambda x: x['relevance'], reverse=True)

class Reasoning:
    def __init__(self, memory: Memory):
        self.memory = memory
        self.logic_patterns = [
            {
                'name': '因果推理',
                'pattern': r'如果.*那么',
                'type': 'causal'
            },
            {
                'name': '类比推理',
                'pattern': r'类似|像|好比',
                'type': 'analogy'
            },
            {
                'name': '归纳推理',
                'pattern': r'所有|都是|���是',
                'type': 'induction'
            }
        ]
        
    def analyze(self, statement: str) -> Dict[str, Any]:
        """分析陈述中的逻辑关系"""
        analysis = {
            'statement': statement,
            'logic_type': None,
            'components': {},
            'confidence': 0.0
        }
        
        # 识别逻辑模式
        for pattern in self.logic_patterns:
            if re.search(pattern['pattern'], statement):
                analysis['logic_type'] = pattern['type']
                if pattern['type'] == 'causal':
                    # 分析因果关系
                    parts = re.split(r'如果|那么', statement)
                    if len(parts) >= 3:
                        analysis['components'] = {
                            'condition': parts[1].strip(),
                            'result': parts[2].strip()
                        }
                        analysis['confidence'] = 0.8
                elif pattern['type'] == 'analogy':
                    # 分析类比关系
                    parts = re.split(r'类似|像|好比', statement)
                    if len(parts) >= 2:
                        analysis['components'] = {
                            'target': parts[0].strip(),
                            'source': parts[1].strip()
                        }
                        analysis['confidence'] = 0.7
                        
        return analysis
        
    def infer(self, context: str) -> Dict[str, Any]:
        """根据上下文进行推理"""
        # 获取相关记忆
        relevant_memories = self.memory.recall(context)
        
        inference = {
            'context': context,
            'conclusion': None,
            'reasoning_path': [],
            'confidence': 0.0
        }
        
        # 分析上下文的逻辑关系
        context_analysis = self.analyze(context)
        
        # 如果找到明确的逻辑关系
        if context_analysis['logic_type']:
            inference['reasoning_path'].append({
                'step': 'logic_identification',
                'detail': f"识别到{context_analysis['logic_type']}逻辑关系"
            })
            
            # 根据逻辑类型进行推理
            if context_analysis['logic_type'] == 'causal':
                # 因果推理
                condition = context_analysis['components'].get('condition')
                if condition:
                    related_memories = self.memory.recall(condition)
                    if related_memories:
                        inference['reasoning_path'].append({
                            'step': 'memory_retrieval',
                            'detail': f"找到{len(related_memories)}条相关记忆"
                        })
                        inference['conclusion'] = self._generate_conclusion(
                            context_analysis, related_memories
                        )
                        inference['confidence'] = 0.7
                        
        return inference
        
    def _generate_conclusion(self, analysis: Dict[str, Any], memories: List[Dict[str, Any]]) -> str:
        """生成推理结论"""
        if analysis['logic_type'] == 'causal':
            condition = analysis['components'].get('condition', '')
            result = analysis['components'].get('result', '')
            
            # 检查记忆中是否有支持的证据
            supporting_evidence = [
                m for m in memories
                if self._text_similarity(m['content'], result) > 0.3
            ]
            
            if supporting_evidence:
                return f"基于过往经验，当{condition}时，很可能{result}"
            else:
                return f"虽然推测{condition}可能导致{result}，但缺乏足够证据支持"
                
        return "无法得出明确结论"
        
    def _text_similarity(self, text1: str, text2: str) -> float:
        """计算两段文本的相似度"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        intersection = words1 & words2
        union = words1 | words2
        return len(intersection) / len(union) if union else 0.0

class DecisionMaking:
    def __init__(self, memory: Memory, reasoning: Reasoning):
        self.memory = memory
        self.reasoning = reasoning
        self.decision_factors = {
            'safety': 0.3,    # 安全性权重
            'efficacy': 0.3,  # 有效性权重
            'ethics': 0.2,    # 伦理性权重
            'novelty': 0.2    # 创新性权重
        }
        
    def make_decision(self, situation: str, options: List[str]) -> Dict[str, Any]:
        """在给定情况下做出决策"""
        decision = {
            'situation': situation,
            'options': options,
            'chosen_option': None,
            'reasoning_process': [],
            'confidence': 0.0
        }
        
        # 获取相关记忆和推理结果
        memories = self.memory.recall(situation)
        inference = self.reasoning.infer(situation)
        
        # 评估每个选项
        option_scores = {}
        for option in options:
            score = self._evaluate_option(option, situation, memories, inference)
            option_scores[option] = score
            decision['reasoning_process'].append({
                'option': option,
                'score': score,
                'factors': self._analyze_factors(option, situation)
            })
            
        # 选择最佳选项
        if option_scores:
            best_option = max(option_scores.items(), key=lambda x: x[1])
            decision['chosen_option'] = best_option[0]
            decision['confidence'] = best_option[1]
            
        return decision
        
    def _evaluate_option(self, option: str, situation: str, 
                        memories: List[Dict[str, Any]], 
                        inference: Dict[str, Any]) -> float:
        """评估单个选项的得分"""
        score = 0.0
        factors = self._analyze_factors(option, situation)
        
        # 根据决策因素计算加权得分
        for factor, weight in self.decision_factors.items():
            score += factors[factor] * weight
            
        # 考虑历史经验
        if memories:
            historical_score = self._evaluate_historical_experience(
                option, memories
            )
            score = 0.7 * score + 0.3 * historical_score
            
        # 考虑推理结果
        if inference['conclusion']:
            reasoning_score = self._evaluate_reasoning_alignment(
                option, inference
            )
            score = 0.8 * score + 0.2 * reasoning_score
            
        return score
        
    def _analyze_factors(self, option: str, situation: str) -> Dict[str, float]:
        """分析决策因素"""
        factors = {}
        
        # 评估安全性
        factors['safety'] = self._evaluate_safety(option, situation)
        
        # 评估有效性
        factors['efficacy'] = self._evaluate_efficacy(option, situation)
        
        # 评估伦理性
        factors['ethics'] = self._evaluate_ethics(option)
        
        # 评估创新性
        factors['novelty'] = self._evaluate_novelty(option)
        
        return factors
        
    def _evaluate_safety(self, option: str, situation: str) -> float:
        """评估选项的安全性"""
        risk_words = {'危险', '伤害', '损失', '风险', '不安全'}
        safety_words = {'安全', '保护', '稳妥', '可靠'}
        
        text = f"{option} {situation}"
        words = set(text.split())
        
        risk_score = len(risk_words & words) * 0.2
        safety_score = len(safety_words & words) * 0.2
        
        return max(0, 1 - risk_score + safety_score)
        
    def _evaluate_efficacy(self, option: str, situation: str) -> float:
        """评估选项的有效性"""
        # 基于相关记忆评估有效性
        memories = self.memory.recall(option)
        if memories:
            success_count = sum(
                1 for m in memories
                if any(word in m['content'] for word in ['成功', '有效', '解决'])
            )
            return min(1.0, success_count / len(memories) + 0.5)
        return 0.5
        
    def _evaluate_ethics(self, option: str) -> float:
        """评估选项的伦理性"""
        unethical_words = {'欺骗', '伤害', '不当', '违规', '非法'}
        ethical_words = {'诚实', '公平', '正当', '合规', '合法'}
        
        words = set(option.split())
        
        unethical_score = len(unethical_words & words) * 0.3
        ethical_score = len(ethical_words & words) * 0.3
        
        return max(0, 1 - unethical_score + ethical_score)
        
    def _evaluate_novelty(self, option: str) -> float:
        """评估选项的创新性"""
        # 检查是否在历史记忆中出现过类似选项
        memories = self.memory.recall(option)
        if memories:
            similarity_scores = [
                self.reasoning._text_similarity(option, m['content'])
                for m in memories
            ]
            avg_similarity = sum(similarity_scores) / len(similarity_scores)
            return 1 - avg_similarity  # 越不相似越创新
        return 1.0  # 完全新颖
        
    def _evaluate_historical_experience(self, option: str, 
                                      memories: List[Dict[str, Any]]) -> float:
        """评估历史经验中该选项的表现"""
        relevant_memories = [
            m for m in memories
            if self.reasoning._text_similarity(option, m['content']) > 0.3
        ]
        
        if not relevant_memories:
            return 0.5  # 无历史经验时返回中性分数
            
        # 分析历史结果
        success_indicators = ['成功', '有效', '好', '解决']
        failure_indicators = ['失败', '无效', '坏', '问题']
        
        success_count = sum(
            1 for m in relevant_memories
            if any(indicator in m['content'] for indicator in success_indicators)
        )
        
        failure_count = sum(
            1 for m in relevant_memories
            if any(indicator in m['content'] for indicator in failure_indicators)
        )
        
        total = len(relevant_memories)
        return (success_count - failure_count) / total + 0.5
        
    def _evaluate_reasoning_alignment(self, option: str, 
                                    inference: Dict[str, Any]) -> float:
        """评估选项与推理结论的一致性"""
        if not inference['conclusion']:
            return 0.5
            
        similarity = self.reasoning._text_similarity(
            option, inference['conclusion']
        )
        return similarity

class CognitiveSystem:
    def __init__(self):
        self.memory = Memory()
        self.reasoning = Reasoning(self.memory)
        self.decision_making = DecisionMaking(self.memory, self.reasoning)
        
    def process_input(self, input_text: str) -> Dict[str, Any]:
        """处理输入并产生认知响应"""
        # 记录输入
        self.memory.add_memory(input_text)
        
        # 分析输入
        analysis = self.reasoning.analyze(input_text)
        
        # 如果是问题，进行推理
        if '?' in input_text or '吗' in input_text:
            inference = self.reasoning.infer(input_text)
        else:
            inference = None
            
        # 如果需要决策
        if '应该' in input_text or '该不该' in input_text:
            # 提取可能的选项
            options = self._extract_options(input_text)
            if options:
                decision = self.decision_making.make_decision(input_text, options)
            else:
                decision = None
        else:
            decision = None
            
        return {
            'input': input_text,
            'analysis': analysis,
            'inference': inference,
            'decision': decision,
            'memories': self.memory.recall(input_text)
        }
        
    def _extract_options(self, text: str) -> List[str]:
        """从文本中提取决策选项"""
        options = []
        
        # 尝试提取"是否"类选项
        if '是否' in text:
            options = ['是', '否']
        # 尝试提取"还是"类选项
        elif '还是' in text:
            parts = text.split('还是')
            if len(parts) >= 2:
                options = [parts[0].split('该')[-1].strip(), parts[1].split('?')[0].strip()]
                
        return options
        
    def save_state(self, filename: str):
        """保存认知系统状态"""
        state = {
            'long_term_memory': dict(self.memory.long_term),
            'associations': {k: list(v) for k, v in self.memory.associations.items()}
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            
    def load_state(self, filename: str):
        """加载认知系统状态"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                state = json.load(f)
                self.memory.long_term = defaultdict(list, state['long_term_memory'])
                self.memory.associations = defaultdict(set, {
                    k: set(v) for k, v in state['associations'].items()
                })
        except FileNotFoundError:
            pass  # 如果文件不存在，使用空白状态 