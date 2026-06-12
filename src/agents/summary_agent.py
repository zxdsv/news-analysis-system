"""
摘要生成Agent - 为新闻生成摘要
"""
from typing import Dict, Any
from src.agents.base_agent import TextAnalysisAgent
from src.config.prompts import (
    SUMMARY_AGENT_SYSTEM_PROMPT,
    SUMMARY_AGENT_USER_TEMPLATE,
)
from loguru import logger


class SummaryAgent(TextAnalysisAgent):
    """摘要生成Agent"""

    def __init__(self, **kwargs):
        super().__init__(
            name="SummaryAgent",
            description="为新闻文章生成高质量的摘要，包括一句话摘要和详细摘要",
            **kwargs
        )

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return SUMMARY_AGENT_SYSTEM_PROMPT

    def get_user_template(self) -> str:
        """获取用户提示词模板"""
        return SUMMARY_AGENT_USER_TEMPLATE

    async def analyze(self, title: str, content: str, **kwargs) -> Dict[str, Any]:
        """
        生成摘要

        Args:
            title: 新闻标题
            content: 新闻内容
            **kwargs: 其他参数

        Returns:
            包含摘要的字典
        """
        logger.info(f"[{self.name}] 开始生成摘要...")
        logger.debug(f"标题: {title[:50]}...")

        result = await super().analyze(title=title, content=content)

        if result.get("status") == "success":
            logger.info(f"[{self.name}] ✓ 摘要生成成功")
            logger.debug(f"一句话摘要: {result.get('one_line_summary', '')[:60]}...")
        else:
            logger.error(f"[{self.name}] ✗ 摘要生成失败: {result.get('error', '未知错误')}")

        return result

    def analyze_sync(self, title: str, content: str, **kwargs) -> Dict[str, Any]:
        """同步版本的摘要生成"""
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.analyze(title=title, content=content, **kwargs))

    def get_one_line_summary(self, result: Dict[str, Any]) -> str:
        """从结果中获取一句话摘要"""
        return result.get("one_line_summary", "摘要生成失败")

    def get_detailed_summary(self, result: Dict[str, Any]) -> str:
        """从结果中获取详细摘要"""
        return result.get("detailed_summary", "详细摘要生成失败")

    def get_key_points(self, result: Dict[str, Any]) -> list:
        """从结果中获取关键要点"""
        return result.get("key_points", [])
