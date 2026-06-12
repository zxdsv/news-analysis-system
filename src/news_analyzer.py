"""
新闻分析器 - 整合所有Agent的主类
"""
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime
from src.agents.pipeline_agent import PipelineAgent, ExecutionMode
from src.agents.summary_agent import SummaryAgent
from src.agents.classify_agent import ClassifyAgent
from src.agents.sentiment_agent import SentimentAgent
from src.agents.extraction_agent import InformationExtractionAgent
from loguru import logger


class NewsAnalyzer:
    """新闻分析器 - 统一的新闻分析接口"""

    def __init__(self):
        """初始化新闻分析器"""
        self.pipeline = PipelineAgent()
        self.pipeline.register_default_agents()
        self._setup_default_workflows()
        logger.info("新闻分析器已初始化")

    def _setup_default_workflows(self) -> None:
        """设置默认工作流"""
        # 完整分析工作流 - 顺序执行
        self.pipeline.create_workflow(
            "full_analysis",
            tasks=[
                {
                    "id": "summary",
                    "agent": "summary",
                    "action": "summarize",
                    "params": {"title": "{title}", "content": "{content}"},
                },
                {
                    "id": "classify",
                    "agent": "classify",
                    "action": "classify",
                    "params": {"title": "{title}", "content": "{content}"},
                },
                {
                    "id": "sentiment",
                    "agent": "sentiment",
                    "action": "analyze",
                    "params": {"text": "{content}"},
                },
                {
                    "id": "extraction",
                    "agent": "extraction",
                    "action": "extract",
                    "params": {"title": "{title}", "content": "{content}"},
                },
            ],
            mode=ExecutionMode.SEQUENTIAL,
        )

        # 快速分析工作流 - 并行执行
        self.pipeline.create_workflow(
            "quick_analysis",
            tasks=[
                {
                    "id": "classify",
                    "agent": "classify",
                    "action": "classify",
                    "params": {"title": "{title}", "content": "{content}"},
                },
                {
                    "id": "sentiment",
                    "agent": "sentiment",
                    "action": "analyze",
                    "params": {"text": "{content}"},
                },
            ],
            mode=ExecutionMode.PARALLEL,
        )

        # 深度分析工作流 - 顺序执行
        self.pipeline.create_workflow(
            "deep_analysis",
            tasks=[
                {
                    "id": "extraction",
                    "agent": "extraction",
                    "action": "extract",
                    "params": {"title": "{title}", "content": "{content}"},
                },
                {
                    "id": "summary",
                    "agent": "summary",
                    "action": "summarize",
                    "params": {"title": "{title}", "content": "{content}"},
                },
            ],
            mode=ExecutionMode.SEQUENTIAL,
        )

        logger.info("默认工作流已设置")

    async def analyze(
        self,
        title: str,
        content: str,
        workflow: str = "full_analysis",
    ) -> Dict[str, Any]:
        """执行新闻分析

        Args:
            title: 新闻标题
            content: 新闻内容
            workflow: 工作流名称

        Returns:
            分析结果
        """
        logger.info(f"开始分析新闻: {title[:50]}...")

        try:
            # 获取工作流
            if workflow not in self.pipeline.workflows:
                logger.error(f"工作流 '{workflow}' 不存在")
                return {
                    "status": "error",
                    "error": f"Workflow '{workflow}' not found",
                }

            # 替换参数中的占位符
            tasks = self._replace_placeholders(
                self.pipeline.workflows[workflow]["tasks"],
                title=title,
                content=content,
            )

            # 运行工作流
            results = await self._run_workflow_tasks(tasks, workflow)

            # 整合结果
            analysis_result = self._integrate_results(results)

            logger.info(f"✓ 新闻分析完成")
            return {
                "status": "success",
                "title": title,
                "workflow": workflow,
                "timestamp": datetime.now().isoformat(),
                "analysis": analysis_result,
            }
        except Exception as e:
            logger.error(f"✗ 新闻分析失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "title": title,
            }

    def analyze_sync(
        self,
        title: str,
        content: str,
        workflow: str = "full_analysis",
    ) -> Dict[str, Any]:
        """同步版本的新闻分析

        Args:
            title: 新闻标题
            content: 新闻内容
            workflow: 工作流名称

        Returns:
            分析结果
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(
            self.analyze(title=title, content=content, workflow=workflow)
        )

    async def batch_analyze(
        self,
        news_list: List[Dict[str, str]],
        workflow: str = "full_analysis",
    ) -> List[Dict[str, Any]]:
        """批量分析新闻

        Args:
            news_list: 新闻列表，每项包含 title 和 content
            workflow: 工作流名称

        Returns:
            分析结果列表
        """
        logger.info(f"开始批量分析 {len(news_list)} 篇新闻")

        tasks = [
            self.analyze(news["title"], news["content"], workflow)
            for news in news_list
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理异常
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({"status": "error", "error": str(result)})
            else:
                processed_results.append(result)

        logger.info(f"✓ 批量分析完成: {len(processed_results)} 篇新闻")
        return processed_results

    def _replace_placeholders(
        self,
        tasks: List[Dict[str, Any]],
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """替换任务中的占位符

        Args:
            tasks: 任务列表
            **kwargs: 替换值

        Returns:
            替换后的任务列表
        """
        import copy
        import json

        new_tasks = copy.deepcopy(tasks)
        for task in new_tasks:
            params = task.get("params", {})
            for key, value in params.items():
                if isinstance(value, str):
                    for placeholder, replacement in kwargs.items():
                        value = value.replace(f"{{{{{placeholder}}}}}", replacement)
                    params[key] = value

        return new_tasks

    async def _run_workflow_tasks(
        self,
        tasks: List[Dict[str, Any]],
        workflow_name: str,
    ) -> Dict[str, Any]:
        """运行工作流任务

        Args:
            tasks: 任务列表
            workflow_name: 工作流名称

        Returns:
            任务结果
        """
        results = {}

        for idx, task in enumerate(tasks, 1):
            agent_name = task.get("agent")
            action = task.get("action")
            params = task.get("params", {})
            task_id = task.get("id", f"task_{idx}")

            if agent_name not in self.pipeline.agents:
                logger.error(f"Agent '{agent_name}' 未找到")
                results[task_id] = {"status": "error", "error": "Agent not found"}
                continue

            try:
                agent = self.pipeline.agents[agent_name]
                logger.debug(f"执行任务: {task_id}")

                if hasattr(agent, action):
                    method = getattr(agent, action)
                    if asyncio.iscoroutinefunction(method):
                        result = await method(**params)
                    else:
                        result = method(**params)
                    results[task_id] = {"status": "success", "data": result}
                    logger.debug(f"✓ 任务 {task_id} 完成")
                else:
                    results[task_id] = {
                        "status": "error",
                        "error": f"Action '{action}' not found",
                    }
            except Exception as e:
                logger.error(f"✗ 任务 {task_id} 失败: {str(e)}")
                results[task_id] = {"status": "error", "error": str(e)}

        return results

    def _integrate_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """整合各Agent的结果

        Args:
            results: 任务结果字典

        Returns:
            整合后的分析结果
        """
        integrated = {}

        # 处理摘要结果
        if "summary" in results and results["summary"].get("status") == "success":
            summary_data = results["summary"].get("data", {})
            integrated["summary"] = summary_data.get("summary")

        # 处理分类结果
        if "classify" in results and results["classify"].get("status") == "success":
            classify_data = results["classify"].get("data", {})
            integrated["category"] = classify_data.get("category")
            integrated["category_confidence"] = classify_data.get("confidence")

        # 处理情感分析结果
        if "sentiment" in results and results["sentiment"].get("status") == "success":
            sentiment_data = results["sentiment"].get("data", {})
            integrated["sentiment"] = sentiment_data.get("sentiment")
            integrated["sentiment_score"] = sentiment_data.get("score")

        # 处理信息抽取结果
        if "extraction" in results and results["extraction"].get("status") == "success":
            extraction_data = results["extraction"].get("data", {})
            integrated["entities"] = extraction_data.get("entities", [])
            integrated["relations"] = extraction_data.get("relations", [])
            integrated["keywords"] = extraction_data.get("keywords", [])
            integrated["events"] = extraction_data.get("events", [])

        return integrated

    def get_available_workflows(self) -> List[str]:
        """获取可用的工作流列表

        Returns:
            工作流名称列表
        """
        return self.pipeline.list_workflows()

    def get_workflow_info(self, workflow_name: str) -> Dict[str, Any]:
        """获取工作流信息

        Args:
            workflow_name: 工作流名称

        Returns:
            工作流信息
        """
        if workflow_name not in self.pipeline.workflows:
            return {"status": "error", "error": "Workflow not found"}

        workflow = self.pipeline.workflows[workflow_name]
        return {
            "name": workflow_name,
            "mode": workflow["mode"].value,
            "tasks": [
                {
                    "id": task.get("id"),
                    "agent": task.get("agent"),
                    "action": task.get("action"),
                }
                for task in workflow["tasks"]
            ],
        }

    def create_custom_workflow(
        self,
        workflow_name: str,
        tasks: List[Dict[str, Any]],
        mode: str = "sequential",
    ) -> Dict[str, Any]:
        """创建自定义工作流

        Args:
            workflow_name: 工作流名称
            tasks: 任务列表
            mode: 执行模式 (sequential/parallel/conditional)

        Returns:
            创建结果
        """
        try:
            execution_mode = ExecutionMode(mode)
            self.pipeline.create_workflow(workflow_name, tasks, execution_mode)
            logger.info(f"✓ 自定义工作流 '{workflow_name}' 已创建")
            return {"status": "success", "message": f"Workflow '{workflow_name}' created"}
        except ValueError:
            logger.error(f"✗ 无效的执行模式: {mode}")
            return {"status": "error", "error": f"Invalid mode: {mode}"}
        except Exception as e:
            logger.error(f"✗ 创建工作流失败: {str(e)}")
            return {"status": "error", "error": str(e)}

    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息

        Returns:
            系统信息
        """
        return {
            "agents": self.pipeline.list_agents(),
            "workflows": self.pipeline.list_workflows(),
            "default_workflows": ["full_analysis", "quick_analysis", "deep_analysis"],
        }
