"""
信息抽取Agent - 从新闻中抽取关键实体和信息
"""
from typing import Dict, Any, List
from src.agents.base_agent import ExtractionAgent
from src.config.prompts import (
    EXTRACTION_AGENT_SYSTEM_PROMPT,
    EXTRACTION_AGENT_USER_TEMPLATE,
)
from loguru import logger


class InformationExtractionAgent(ExtractionAgent):
    """新闻信息抽取Agent"""

    def __init__(self, **kwargs):
        super().__init__(
            name="InformationExtractionAgent",
            description="从新闻文章中抽取关键信息，包括人物、地点、机构、事件等实体",
            **kwargs
        )

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return EXTRACTION_AGENT_SYSTEM_PROMPT

    def get_user_template(self) -> str:
        """获取用户提示词模板"""
        return EXTRACTION_AGENT_USER_TEMPLATE

    async def extract(self, title: str, content: str, **kwargs) -> Dict[str, Any]:
        """
        从新闻中抽取信息

        Args:
            title: 新闻标题
            content: 新闻内容
            **kwargs: 其他参数

        Returns:
            包含抽取结果的字典
        """
        logger.info(f"[{self.name}] 开始进行信息抽取...")
        logger.debug(f"标题: {title[:50]}...")

        result = await super().extract(title=title, content=content)

        if result.get("status") == "success":
            entities_count = len(result.get("entities", []))
            logger.info(f"[{self.name}] ✓ 信息抽取完成: 抽取 {entities_count} 个实体")
        else:
            logger.error(f"[{self.name}] ✗ 信息抽取失败: {result.get('error', '未知错误')}")

        return result

    def extract_sync(self, title: str, content: str, **kwargs) -> Dict[str, Any]:
        """同步版本的信息抽取"""
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.extract(title=title, content=content, **kwargs))

    def get_entities(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取所有抽取的实体"""
        return result.get("entities", [])

    def get_persons(self, result: Dict[str, Any]) -> List[str]:
        """获取人物实体"""
        entities = self.get_entities(result)
        return [e.get("name") for e in entities if e.get("type") == "PERSON"]

    def get_locations(self, result: Dict[str, Any]) -> List[str]:
        """获取地点实体"""
        entities = self.get_entities(result)
        return [e.get("name") for e in entities if e.get("type") == "LOCATION"]

    def get_organizations(self, result: Dict[str, Any]) -> List[str]:
        """获取机构实体"""
        entities = self.get_entities(result)
        return [e.get("name") for e in entities if e.get("type") == "ORGANIZATION"]

    def get_events(self, result: Dict[str, Any]) -> List[str]:
        """获取事件信息"""
        return result.get("events", [])

    def get_relations(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取实体间的关系"""
        return result.get("relations", [])

    def get_time_expressions(self, result: Dict[str, Any]) -> List[str]:
        """获取时间表达式"""
        return result.get("time_expressions", [])

    def get_keywords(self, result: Dict[str, Any]) -> List[str]:
        """获取关键词"""
        return result.get("keywords", [])

    def filter_entities_by_type(self, result: Dict[str, Any], entity_type: str) -> List[Dict[str, Any]]:
        """按类型筛选实体

        Args:
            result: 抽取结果
            entity_type: 实体类型 (PERSON, LOCATION, ORGANIZATION, etc.)

        Returns:
            筛选后的实体列表
        """
        entities = self.get_entities(result)
        return [e for e in entities if e.get("type") == entity_type]

    def get_entity_by_name(self, result: Dict[str, Any], name: str) -> Dict[str, Any]:
        """按名称获取实体

        Args:
            result: 抽取结果
            name: 实体名称

        Returns:
            匹配的实体字典，未找到则返回空字典
        """
        entities = self.get_entities(result)
        for entity in entities:
            if entity.get("name") == name:
                return entity
        return {}

    def get_entity_relations(self, result: Dict[str, Any], entity_name: str) -> List[Dict[str, Any]]:
        """获取特定实体的所有关系

        Args:
            result: 抽取结果
            entity_name: 实体名称

        Returns:
            包含该实体的所有关系列表
        """
        relations = self.get_relations(result)
        return [
            r for r in relations
            if r.get("subject") == entity_name or r.get("object") == entity_name
        ]

    def get_summary_statistics(self, result: Dict[str, Any]) -> Dict[str, int]:
        """获取抽取结果的统计信息

        Returns:
            包含各类实体数量的统计字典
        """
        entities = self.get_entities(result)
        stats = {
            "total_entities": len(entities),
            "persons": len(self.get_persons(result)),
            "locations": len(self.get_locations(result)),
            "organizations": len(self.get_organizations(result)),
            "events": len(self.get_events(result)),
            "relations": len(self.get_relations(result)),
            "keywords": len(self.get_keywords(result)),
        }
        return stats
