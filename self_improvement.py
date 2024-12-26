import ast
import inspect
import textwrap
import importlib
import os
import json
from typing import Dict, List, Any, Tuple
import openai
from collections import defaultdict

class CodeAnalyzer:
    """代码分析器：分析代码结构和性能"""
    def __init__(self):
        self.code_metrics = defaultdict(dict)
        self.performance_logs = []
        self.optimization_history = []
        
    def analyze_code(self, module_name: str) -> Dict[str, Any]:
        """分析模块代码"""
        try:
            module = importlib.import_module(module_name)
            source = inspect.getsource(module)
            tree = ast.parse(source)
            
            analysis = {
                'module': module_name,
                'classes': self._analyze_classes(tree),
                'functions': self._analyze_functions(tree),
                'complexity': self._calculate_complexity(tree),
                'metrics': self._calculate_metrics(tree)
            }
            
            self.code_metrics[module_name] = analysis
            return analysis
            
        except Exception as e:
            print(f"代码分析错误: {e}")
            return {}
            
    def _analyze_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """分析类定义"""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    'name': node.name,
                    'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                    'attributes': [a.targets[0].id for a in node.body 
                                 if isinstance(a, ast.Assign)],
                    'complexity': self._calculate_complexity(node)
                }
                classes.append(class_info)
        return classes
        
    def _analyze_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """分析函数定义"""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    'name': node.name,
                    'args': [a.arg for a in node.args.args],
                    'complexity': self._calculate_complexity(node),
                    'returns': self._analyze_returns(node)
                }
                functions.append(func_info)
        return functions
        
    def _calculate_complexity(self, node: ast.AST) -> int:
        """计算代码复杂度"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.FunctionDef,
                                ast.ClassDef, ast.Try, ast.ExceptHandler)):
                complexity += 1
        return complexity
        
    def _calculate_metrics(self, tree: ast.AST) -> Dict[str, int]:
        """计算代码度量指标"""
        metrics = {
            'lines': len(ast.unparse(tree).split('\n')),
            'classes': len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
            'functions': len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
            'imports': len([n for n in ast.walk(tree) if isinstance(n, ast.Import)])
        }
        return metrics
        
    def _analyze_returns(self, node: ast.FunctionDef) -> List[str]:
        """分析函数返回值"""
        returns = []
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value:
                returns.append(ast.unparse(child.value))
        return returns
        
    def log_performance(self, function_name: str, execution_time: float,
                       memory_usage: float, success: bool):
        """记录性能数据"""
        log = {
            'function': function_name,
            'execution_time': execution_time,
            'memory_usage': memory_usage,
            'success': success,
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.performance_logs.append(log)

class CodeOptimizer:
    """代码优化器：优化代码结构和性能"""
    def __init__(self, analyzer: CodeAnalyzer):
        self.analyzer = analyzer
        self.optimization_rules = self._load_optimization_rules()
        self.improvement_history = []
        
    def _load_optimization_rules(self) -> Dict[str, Any]:
        """加载优化规则"""
        rules = {
            'complexity': {
                'threshold': 10,
                'action': 'refactor'
            },
            'performance': {
                'execution_time_threshold': 1.0,
                'memory_usage_threshold': 100
            },
            'style': {
                'max_line_length': 80,
                'max_function_length': 50
            }
        }
        return rules
        
    def suggest_improvements(self, module_name: str) -> List[Dict[str, Any]]:
        """提出改进建议"""
        analysis = self.analyzer.code_metrics.get(module_name, {})
        if not analysis:
            return []
            
        suggestions = []
        
        # 检查复杂度
        for class_info in analysis.get('classes', []):
            if class_info['complexity'] > self.optimization_rules['complexity']['threshold']:
                suggestions.append({
                    'type': 'complexity',
                    'target': f"类 {class_info['name']}",
                    'suggestion': '建议将复杂的类拆分为多个更小的类',
                    'priority': 'high'
                })
                
        # 检查性能
        for log in self.analyzer.performance_logs:
            if log['execution_time'] > self.optimization_rules['performance']['execution_time_threshold']:
                suggestions.append({
                    'type': 'performance',
                    'target': log['function'],
                    'suggestion': '函数执行时间过长，建议优化算法或使用缓存',
                    'priority': 'medium'
                })
                
        return suggestions
        
    def generate_optimization_code(self, suggestion: Dict[str, Any]) -> str:
        """生成优化代码"""
        if suggestion['type'] == 'complexity':
            return self._generate_refactoring_code(suggestion)
        elif suggestion['type'] == 'performance':
            return self._generate_performance_optimization_code(suggestion)
        return ""
        
    def _generate_refactoring_code(self, suggestion: Dict[str, Any]) -> str:
        """生成重构代码"""
        # 使用GPT生成重构建议
        prompt = f"""
        请帮我重构以下代码，目标是降低复杂度：
        目标：{suggestion['target']}
        建议：{suggestion['suggestion']}
        
        请提供具体的重构代码和重构说明。
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个代码重构专家，专注于改进代码质量和可维护性。"},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message['content']
        except:
            return "无法生成重构代码，请检查API配置。"
            
    def _generate_performance_optimization_code(self, suggestion: Dict[str, Any]) -> str:
        """生成性能优化代码"""
        # 使用GPT生成性能优化建议
        prompt = f"""
        请帮我优化以下代码的性能：
        函数：{suggestion['target']}
        问题：{suggestion['suggestion']}
        
        请提供具体的优化代码和优化说明。
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个性能优化专家，专注于提升代码执行效率。"},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message['content']
        except:
            return "无法生成优化代码，请检查API配置。"

class SelfImprovement:
    """自我改进系统：分析、优化和改进机器人的能力"""
    def __init__(self, openai_api_key: str = None):
        self.analyzer = CodeAnalyzer()
        self.optimizer = CodeOptimizer(self.analyzer)
        self.improvement_log = []
        self.openai_api_key = openai_api_key
        
        if openai_api_key:
            openai.api_key = openai_api_key
            
    def analyze_self(self) -> Dict[str, Any]:
        """分析自身代码"""
        modules = [
            'simple_bot',
            'cognitive_system',
            'emotional_system',
            'self_improvement'
        ]
        
        analysis = {}
        for module in modules:
            analysis[module] = self.analyzer.analyze_code(module)
            
        return analysis
        
    def suggest_improvements(self) -> List[Dict[str, Any]]:
        """提出改进建议"""
        suggestions = []
        analysis = self.analyze_self()
        
        for module, module_analysis in analysis.items():
            module_suggestions = self.optimizer.suggest_improvements(module)
            suggestions.extend(module_suggestions)
            
        return suggestions
        
    def implement_improvement(self, suggestion: Dict[str, Any]) -> bool:
        """实现改进"""
        try:
            # 生成优化代码
            optimization_code = self.optimizer.generate_optimization_code(suggestion)
            
            if not optimization_code:
                return False
                
            # 记录改进
            improvement = {
                'timestamp': datetime.datetime.now().isoformat(),
                'suggestion': suggestion,
                'optimization_code': optimization_code
            }
            self.improvement_log.append(improvement)
            
            # TODO: 实现自动代码更新机制
            # 目前仅生成建议，需要人工审查和应用
            
            return True
            
        except Exception as e:
            print(f"实现改进时出错: {e}")
            return False
            
    def generate_new_feature(self, feature_description: str) -> str:
        """生成新功能代码"""
        try:
            # 使用GPT生成新功能代码
            prompt = f"""
            请帮我为机器人开发新功能：
            功能描述：{feature_description}
            
            要求：
            1. 代码应该符合Python最佳实践
            2. 包含必要的注释和文档
            3. 包含错误处理
            4. 考虑与现有系统的集成
            
            请提供完整的实现代码。
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个Python专家，专注于开发智能机器人功能。"},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.choices[0].message['content']
            
        except Exception as e:
            print(f"生成新功能时出错: {e}")
            return ""
            
    def save_state(self, filename: str = 'self_improvement_state.json'):
        """保存改进状态"""
        state = {
            'improvement_log': self.improvement_log,
            'code_metrics': self.analyzer.code_metrics,
            'performance_logs': self.analyzer.performance_logs
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            
    def load_state(self, filename: str = 'self_improvement_state.json'):
        """加载改进状态"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                state = json.load(f)
                self.improvement_log = state.get('improvement_log', [])
                self.analyzer.code_metrics = state.get('code_metrics', {})
                self.analyzer.performance_logs = state.get('performance_logs', []) 