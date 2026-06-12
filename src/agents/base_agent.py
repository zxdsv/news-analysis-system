"""
基础Agent类 - 所有具体Agent的父类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from langchain.llms.base import BaseLLM
from langchain.chat_models import ChatOpenAI
import json
import re
from loguru import logger
from src.config.settings import settings


class BaseAgent(ABC):
    """基础Agent抽象类"""

    def __init__(
        self,
        name: str,
        description: str,
        llm: Optional[BaseLLM] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        """
        初始化Agent

        Args:
            name: Agent名称
            description: Agent描述
            llm: 语言模型实例
            temperature: 模型温度参数
            max_tokens: 最大令牌数
        """
        self.name = name
        self.description = description
        self.temperature = temperature
        self.max_tokens = max_tokens

        # 初始化LLM
        if llm is None:
            self.llm = self._initialize_llm()
        else:
            self.llm = llm

        logger.info(f"✓ Agent '{self.name}' 已初始化")

    def _initialize_llm(self) -> BaseLLM:
        """初始化DeepSeek LLM"""
        try:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model_name=settings.deepseek_model,
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_api_url,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            logger.debug(f"✓ DeepSeek LLM 已初始化")
            return llm
        except Exception as e:
            logger.error(f"✗ LLM初始化失败: {str(e)}")
            raise

    @abstractmethod
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        pass

    @abstractmethod
    def get_user_template(self) -> str:
        """获取用户提示词模板"""
        pass

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        解析LLM返回的JSON响应

        Args:
            response: 模型返回的文本

        Returns:
            解析后的字典
        """
        try:
            # 尝试直接解析
            return json.loads(response)
        except json.JSONDecodeError:
            # 尝试提取JSON块
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            logger.warning(f"无法解析JSON响应: {response[:100]}")
            return {"error": "JSON解析失败", "raw_response": response}

    def _format_user_prompt(self, **kwargs) -> str:
        """格式化用户提示词"""
        template = self.get_user_template()
        return template.format(**kwargs)

    async def analyze(self, **kwargs) -> Dict[str, Any]:
        """
        执行分析 - 异步方法

        Args:
            **kwargs: 传递给提示词模板的参数

        Returns:
            分析结果字典
        """
        try:
            system_prompt = self.get_system_prompt()
            user_prompt = self._format_user_prompt(**kwargs)

            logger.debug(f"[{self.name}] 发送请求到DeepSeek...")

            # 调用LLM
            from langchain.schema import HumanMessage, SystemMessage

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]

            response = self.llm.invoke(messages)
            response_text = response.content

            logger.debug(f"[{self.name}] 收到响应: {response_text[:100]}...")

            # 解析响应
            result = self._parse_json_response(response_text)

            # 添加元数据
            result["agent_name"] = self.name
            result["status"] = "success"

            return result

        except Exception as e:
            logger.error(f"[{self.name}] 分析失败: {str(e)}")
            return {
                "agent_name": self.name,
                "status": "error",
                "error": str(e),
            }

    def analyze_sync(self, **kwargs) -> Dict[str, Any]:
        """
        执行分析 - 同步方法（简化版）

        Args:
            **kwargs: 传递给提示词模板的参数

        Returns:
            分析结果字典
        """
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.analyze(**kwargs))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"


class TextAnalysisAgent(BaseAgent):
    """文本分析Agent基类"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _extract_key_info(self, text: str, max_length: int = 500) -> str:
        """
        提取文本关键信息

        Args:
            text: 输入文本
            max_length: 最大长度

        Returns:
            提取的关键信息
        """
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text


class ClassificationAgent(BaseAgent):
    """分类Agent基类"""

    def __init__(self, categories: Optional[List[str]] = None, *args, **kwargs):
        self.categories = (
            categories
            or [
                "政治",
                "经济",
                "科技",
                "社会",
                "文化",
                "环境",
                "其他",
            ]
        )
        super().__init__(*args, **kwargs)

    def validate_category(self, category: str) -> bool:
        """验证分类是否有效"""
        return category in self.categories


class RankingAgent(BaseAgent):
    """评分/排名Agent基类"""

    def __init__(self, score_range: tuple = (0, 10), *args, **kwargs):
        self.score_range = score_range
        super().__init__(*args, **kwargs)

    def validate_score(self, score: float) -> bool:
        """验证分数是否在有效范围内"""
        return self.score_range[0] <= score <= self.score_range[1]


class VerificationAgent(BaseAgent):
    """验证/校验Agent基类"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_credibility_level(self, score: float) -> str:
        """获取可信度级别"""
        if score >= 0.8:
            return "很高"
        elif score >= 0.6:
            return "中等"
        elif score >= 0.4:
            return "较低"
        else:
            return "很低"
