"""
情感分析Agent - 对新闻进行情感倾向分析
"""
from typing import Dict, Any
from src.agents.base_agent import SentimentAgent
from src.config.prompts import (
    SENTIMENT_AGENT_SYSTEM_PROMPT,
    SENTIMENT_AGENT_USER_TEMPLATE,
)
from loguru import logger


class SentimentAnalysisAgent(SentimentAgent):
    """新闻情感分析Agent"""

    def __init__(self, **kwargs):
        super().__init__(
            name="SentimentAnalysisAgent",
            description="分析新闻文章的情感倾向，包括正面、负面和中性情感",
            **kwargs
        )

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return SENTIMENT_AGENT_SYSTEM_PROMPT

    def get_user_template(self) -> str:
        """获取用户提示词模板"""
        return SENTIMENT_AGENT_USER_TEMPLATE

    async def analyze(self, title: str, content: str, **kwargs) -> Dict[str, Any]:
        """
        分析新闻情感

        Args:
            title: 新闻标题
            content: 新闻内容
            **kwargs: 其他参数

        Returns:
            包含情感分析结果的字典
        """
        logger.info(f"[{self.name}] 开始进行情感分析...")
        logger.debug(f"标题: {title[:50]}...")

        result = await super().analyze(title=title, content=content)

        if result.get("status") == "success":
            sentiment = result.get("sentiment", "未知")
            score = result.get("sentiment_score", 0)
            logger.info(f"[{self.name}] ✓ 情感分析完成: {sentiment} (得分: {score:.2f})")
        else:
            logger.error(f"[{self.name}] ✗ 情感分析失败: {result.get('error', '未知错误')}")

        return result

    def analyze_sync(self, title: str, content: str, **kwargs) -> Dict[str, Any]:
        """同步版本的情感分析"""
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.analyze(title=title, content=content, **kwargs))

    def get_sentiment(self, result: Dict[str, Any]) -> str:
        """获取情感倾向"""
        return result.get("sentiment", "未知")

    def get_sentiment_score(self, result: Dict[str, Any]) -> float:
        """获取情感分数 (-1.0 到 1.0)"""
        return result.get("sentiment_score", 0.0)

    def get_emotion_distribution(self, result: Dict[str, Any]) -> Dict[str, float]:
        """获取情感分布"""
        return result.get("emotion_distribution", {})

    def get_key_emotional_phrases(self, result: Dict[str, Any]) -> list:
        """获取关键情感短语"""
        return result.get("key_emotional_phrases", [])

    def is_positive(self, result: Dict[str, Any], threshold: float = 0.3) -> bool:
        """判断是否为正面情感"""
        score = self.get_sentiment_score(result)
        return score > threshold

    def is_negative(self, result: Dict[str, Any], threshold: float = -0.3) -> bool:
        """判断是否为负面情感"""
        score = self.get_sentiment_score(result)
        return score < threshold

    def is_neutral(self, result: Dict[str, Any], threshold: float = 0.3) -> bool:
        """判断是否为中性情感"""
        score = self.get_sentiment_score(result)
        return -threshold <= score <= threshold
