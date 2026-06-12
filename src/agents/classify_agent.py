"""
分类Agent - 对新闻进行自动分类
"""
from typing import Dict, Any, List, Optional
from src.agents.base_agent import ClassificationAgent
from src.config.prompts import (
    CLASSIFY_AGENT_SYSTEM_PROMPT,
    CLASSIFY_AGENT_USER_TEMPLATE,
)
from loguru import logger


class ClassifyAgent(ClassificationAgent):
    """新闻分类Agent"""

    def __init__(
        self,
        categories: Optional[List[str]] = None,
        **kwargs
    ):
        if categories is None:
            categories = [
                "政治",
                "经济",
                "科技",
                "社会",
                "文化",
                "环境",
                "其他",
            ]

        super().__init__(
            name="ClassifyAgent",
            description="对新闻文章进行精确分类，并提供置信度评分",
            categories=categories,
            **kwargs
        )

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return CLASSIFY_AGENT_SYSTEM_PROMPT

    def get_user_template(self) -> str:
        """获取用户提示词模板"""
        return CLASSIFY_AGENT_USER_TEMPLATE

    async def analyze(self, title: str, content: str, **kwargs) -> Dict[str, Any]:
        """
        对新闻进行分类

        Args:
            title: 新闻标题
            content: 新闻内容
            **kwargs: 其他参数

        Returns:
            包含分类结果的字典
        """
        logger.info(f"[{self.name}] 开始分类...")
        logger.debug(f"标题: {title[:50]}...")

        result = await super().analyze(title=title, content=content)

        if result.get("status") == "success":
            category = result.get("primary_category", "未知")
            confidence = result.get("confidence", 0)
            logger.info(f"[{self.name}] ✓ 分类完成: {category} (置信度: {confidence:.2%})")
        else:
            logger.error(f"[{self.name}] ✗ 分类失败: {result.get('error', '未知错误')}")

        return result

    def analyze_sync(self, title: str, content: str, **kwargs) -> Dict[str, Any]:
        """同步版本的分类"""
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.analyze(title=title, content=content, **kwargs))

    def get_primary_category(self, result: Dict[str, Any]) -> str:
        """获取主分类"""
        return result.get("primary_category", "未知")

    def get_confidence(self, result: Dict[str, Any]) -> float:
        """获取置信度"""
        return result.get("confidence", 0.0)

    def get_secondary_category(self, result: Dict[str, Any]) -> Optional[str]:
        """获取次分类"""
        return result.get("secondary_category", None)

    def get_reasoning(self, result: Dict[str, Any]) -> str:
        """获取分类理由"""
        return result.get("reasoning", "无分类理由")

    def is_high_confidence(self, result: Dict[str, Any], threshold: float = 0.7) -> bool:
        """判断置信度是否足够高"""
        confidence = self.get_confidence(result)
        return confidence >= threshold
