"""
管道编排Agent - 协调和管理多个Agent的工作流程
"""
from typing import Dict, Any, List, Optional, Callable, Coroutine
from enum import Enum
import asyncio
from src.agents.base_agent import Agent
from src.agents.summary_agent import SummaryAgent
from src.agents.classify_agent import ClassifyAgent
from src.agents.sentiment_agent import SentimentAgent
from src.agents.extraction_agent import InformationExtractionAgent
from loguru import logger


class ExecutionMode(Enum):
    """执行模式"""
    SEQUENTIAL = "sequential"  # 顺序执行
    PARALLEL = "parallel"      # 并行执行
    CONDITIONAL = "conditional"  # 条件执行


class PipelineAgent(Agent):
    """管道编排Agent - 协调多个Agent的工作流程"""

    def __init__(self, **kwargs):
        super().__init__(
            name="PipelineAgent",
            description="协调和管理多个Agent的工作流程，支持顺序、并行、条件执行等模式",
            **kwargs
        )
        self.agents: Dict[str, Agent] = {}
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.results: Dict[str, Dict[str, Any]] = {}

    def register_agent(self, agent_name: str, agent: Agent) -> None:
        """注册Agent

        Args:
            agent_name: Agent标识名
            agent: Agent实例
        """
        self.agents[agent_name] = agent
        logger.info(f"[{self.name}] 已注册Agent: {agent_name}")

    def register_default_agents(self) -> None:
        """注册默认Agent集合"""
        self.register_agent("summary", SummaryAgent())
        self.register_agent("classify", ClassifyAgent())
        self.register_agent("sentiment", SentimentAgent())
        self.register_agent("extraction", InformationExtractionAgent())
        logger.info(f"[{self.name}] 已注册所有默认Agent")

    def create_workflow(
        self,
        workflow_name: str,
        tasks: List[Dict[str, Any]],
        mode: ExecutionMode = ExecutionMode.SEQUENTIAL,
    ) -> None:
        """创建工作流

        Args:
            workflow_name: 工作流名称
            tasks: 任务列表，每个任务包含agent、action、params等
            mode: 执行模式
        """
        self.workflows[workflow_name] = {
            "tasks": tasks,
            "mode": mode,
        }
        logger.info(f"[{self.name}] 已创建工作流: {workflow_name} (模式: {mode.value})")

    async def execute_sequential(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """顺序执行任务

        Args:
            tasks: 任务列表

        Returns:
            执行结果
        """
        logger.info(f"[{self.name}] 开始顺序执行 {len(tasks)} 个任务")
        results = {}

        for idx, task in enumerate(tasks, 1):
            agent_name = task.get("agent")
            action = task.get("action")
            params = task.get("params", {})
            task_id = task.get("id", f"task_{idx}")

            if agent_name not in self.agents:
                logger.error(f"[{self.name}] Agent '{agent_name}' 未找到")
                results[task_id] = {"status": "error", "error": "Agent not found"}
                continue

            try:
                agent = self.agents[agent_name]
                logger.info(f"[{self.name}] 执行任务 {idx}/{len(tasks)}: {task_id}")

                result = await self._execute_agent_action(agent, action, params)
                results[task_id] = result
                logger.info(f"[{self.name}] ✓ 任务 {task_id} 完成")
            except Exception as e:
                logger.error(f"[{self.name}] ✗ 任务 {task_id} 失败: {str(e)}")
                results[task_id] = {"status": "error", "error": str(e)}

        self.results = results
        return results

    async def execute_parallel(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """并行执行任务

        Args:
            tasks: 任务列表

        Returns:
            执行结果
        """
        logger.info(f"[{self.name}] 开始并行执行 {len(tasks)} 个任务")
        results = {}
        coroutines = []
        task_ids = []

        for idx, task in enumerate(tasks, 1):
            agent_name = task.get("agent")
            action = task.get("action")
            params = task.get("params", {})
            task_id = task.get("id", f"task_{idx}")
            task_ids.append(task_id)

            if agent_name not in self.agents:
                logger.error(f"[{self.name}] Agent '{agent_name}' 未找到")
                results[task_id] = {"status": "error", "error": "Agent not found"}
                continue

            agent = self.agents[agent_name]
            coroutines.append(self._execute_agent_action(agent, action, params))

        if coroutines:
            try:
                execution_results = await asyncio.gather(*coroutines, return_exceptions=True)
                for task_id, result in zip(task_ids, execution_results):
                    if isinstance(result, Exception):
                        logger.error(f"[{self.name}] ✗ 任务 {task_id} 失败: {str(result)}")
                        results[task_id] = {"status": "error", "error": str(result)}
                    else:
                        results[task_id] = result
                        logger.info(f"[{self.name}] ✓ 任务 {task_id} 完成")
            except Exception as e:
                logger.error(f"[{self.name}] 并行执行出错: {str(e)}")

        self.results = results
        return results

    async def execute_conditional(
        self,
        tasks: List[Dict[str, Any]],
        conditions: Dict[str, Callable[[Dict[str, Any]], bool]],
    ) -> Dict[str, Any]:
        """条件执行任务

        Args:
            tasks: 任务列表
            conditions: 条件函数字典

        Returns:
            执行结果
        """
        logger.info(f"[{self.name}] 开始条件执行 {len(tasks)} 个任务")
        results = {}

        for idx, task in enumerate(tasks, 1):
            task_id = task.get("id", f"task_{idx}")
            condition_name = task.get("condition")

            # 检查条件
            if condition_name and condition_name in conditions:
                condition_func = conditions[condition_name]
                if not condition_func(self.results):
                    logger.info(f"[{self.name}] 任务 {task_id} 不满足条件，跳过")
                    results[task_id] = {"status": "skipped", "reason": "condition not met"}
                    continue

            agent_name = task.get("agent")
            action = task.get("action")
            params = task.get("params", {})

            if agent_name not in self.agents:
                logger.error(f"[{self.name}] Agent '{agent_name}' 未找到")
                results[task_id] = {"status": "error", "error": "Agent not found"}
                continue

            try:
                agent = self.agents[agent_name]
                logger.info(f"[{self.name}] 执行任务 {idx}/{len(tasks)}: {task_id}")

                result = await self._execute_agent_action(agent, action, params)
                results[task_id] = result
                logger.info(f"[{self.name}] ✓ 任务 {task_id} 完成")
            except Exception as e:
                logger.error(f"[{self.name}] ✗ 任务 {task_id} 失败: {str(e)}")
                results[task_id] = {"status": "error", "error": str(e)}

        self.results = results
        return results

    async def _execute_agent_action(
        self,
        agent: Agent,
        action: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """执行Agent的特定动作

        Args:
            agent: Agent实例
            action: 动作名称
            params: 参数字典

        Returns:
            执行结果
        """
        try:
            # 获取Agent的方法
            if hasattr(agent, action):
                method = getattr(agent, action)
                if asyncio.iscoroutinefunction(method):
                    result = await method(**params)
                else:
                    result = method(**params)
                return {"status": "success", "data": result}
            else:
                return {"status": "error", "error": f"Action '{action}' not found"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def run_workflow(
        self,
        workflow_name: str,
        conditions: Optional[Dict[str, Callable]] = None,
    ) -> Dict[str, Any]:
        """运行工作流

        Args:
            workflow_name: 工作流名称
            conditions: 条件函数字典（仅在条件执行模式下使用）

        Returns:
            执行结果
        """
        if workflow_name not in self.workflows:
            logger.error(f"[{self.name}] 工作流 '{workflow_name}' 未找到")
            return {"status": "error", "error": "Workflow not found"}

        workflow = self.workflows[workflow_name]
        tasks = workflow["tasks"]
        mode = workflow["mode"]

        logger.info(f"[{self.name}] 开始运行工作流: {workflow_name}")

        try:
            if mode == ExecutionMode.SEQUENTIAL:
                results = await self.execute_sequential(tasks)
            elif mode == ExecutionMode.PARALLEL:
                results = await self.execute_parallel(tasks)
            elif mode == ExecutionMode.CONDITIONAL:
                results = await self.execute_conditional(tasks, conditions or {})
            else:
                return {"status": "error", "error": "Unknown execution mode"}

            logger.info(f"[{self.name}] ✓ 工作流 '{workflow_name}' 完成")
            return {
                "status": "success",
                "workflow": workflow_name,
                "results": results,
            }
        except Exception as e:
            logger.error(f"[{self.name}] ✗ 工作流 '{workflow_name}' 失败: {str(e)}")
            return {"status": "error", "error": str(e)}

    def get_result(self, task_id: str) -> Dict[str, Any]:
        """获取特定任务的结果

        Args:
            task_id: 任务ID

        Returns:
            任务结果
        """
        return self.results.get(task_id, {})

    def get_all_results(self) -> Dict[str, Dict[str, Any]]:
        """获取所有任务的结果

        Returns:
            所有结果字典
        """
        return self.results

    def get_workflow_summary(self, workflow_name: str) -> Dict[str, Any]:
        """获取工作流的执行摘要

        Args:
            workflow_name: 工作流名称

        Returns:
            执行摘要
        """
        if workflow_name not in self.workflows:
            return {"status": "error", "error": "Workflow not found"}

        total_tasks = len(self.workflows[workflow_name]["tasks"])
        successful = sum(
            1 for r in self.results.values()
            if r.get("status") == "success"
        )
        failed = sum(
            1 for r in self.results.values()
            if r.get("status") == "error"
        )
        skipped = sum(
            1 for r in self.results.values()
            if r.get("status") == "skipped"
        )

        return {
            "workflow": workflow_name,
            "total_tasks": total_tasks,
            "successful": successful,
            "failed": failed,
            "skipped": skipped,
            "mode": self.workflows[workflow_name]["mode"].value,
        }

    def list_workflows(self) -> List[str]:
        """列出所有工作流

        Returns:
            工作流名称列表
        """
        return list(self.workflows.keys())

    def list_agents(self) -> List[str]:
        """列出所有已注册的Agent

        Returns:
            Agent名称列表
        """
        return list(self.agents.keys())
