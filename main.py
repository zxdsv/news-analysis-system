"""
新闻分析系统 - 主程序入口和CLI接口
"""
import asyncio
import json
from typing import Optional, List
import click
from pathlib import Path
from datetime import datetime
from src.news_analyzer import NewsAnalyzer
from loguru import logger


# 配置日志
logger.remove()
logger.add(
    "logs/news_analysis_{time}.log",
    rotation="500 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
)
logger.add(
    lambda msg: click.echo(msg, err=False),
    format="{time:HH:mm:ss} | {level: <8} | {message}",
)


class NewsAnalysisApp:
    """新闻分析应用程序"""

    def __init__(self):
        """初始化应用程序"""
        self.analyzer = NewsAnalyzer()
        logger.info("新闻分析应用程序已初始化")

    async def analyze_news(
        self,
        title: str,
        content: str,
        workflow: str = "full_analysis",
    ) -> dict:
        """分析单篇新闻

        Args:
            title: 新闻标题
            content: 新闻内容
            workflow: 工作流名称

        Returns:
            分析结果
        """
        return await self.analyzer.analyze(title, content, workflow)

    async def analyze_file(
        self,
        file_path: str,
        workflow: str = "full_analysis",
    ) -> dict:
        """分析文件中的新闻

        Args:
            file_path: 文件路径（JSON格式）
            workflow: 工作流名称

        Returns:
            分析结果
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                # 批量分析
                results = await self.analyzer.batch_analyze(data, workflow)
                return {
                    "status": "success",
                    "total": len(results),
                    "results": results,
                }
            elif isinstance(data, dict):
                # 单篇分析
                result = await self.analyzer.analyze(
                    data.get("title", ""),
                    data.get("content", ""),
                    workflow,
                )
                return result
            else:
                return {"status": "error", "error": "Invalid file format"}
        except FileNotFoundError:
            logger.error(f"文件不存在: {file_path}")
            return {"status": "error", "error": f"File not found: {file_path}"}
        except json.JSONDecodeError:
            logger.error(f"JSON 解析失败: {file_path}")
            return {"status": "error", "error": "Invalid JSON format"}
        except Exception as e:
            logger.error(f"分析失败: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def analyze_batch(
        self,
        news_list: List[dict],
        workflow: str = "full_analysis",
    ) -> dict:
        """批量分析新闻

        Args:
            news_list: 新闻列表
            workflow: 工作流名称

        Returns:
            分析结果
        """
        results = await self.analyzer.batch_analyze(news_list, workflow)
        return {
            "status": "success",
            "total": len(results),
            "results": results,
        }

    def get_workflows(self) -> dict:
        """获取可用工作流

        Returns:
            工作流列表
        """
        workflows = self.analyzer.get_available_workflows()
        workflow_info = {}

        for workflow in workflows:
            info = self.analyzer.get_workflow_info(workflow)
            workflow_info[workflow] = info

        return {
            "status": "success",
            "workflows": workflow_info,
        }

    def get_system_info(self) -> dict:
        """获取系统信息

        Returns:
            系统信息
        """
        return {
            "status": "success",
            "info": self.analyzer.get_system_info(),
        }

    def save_results(self, results: dict, output_file: str) -> dict:
        """保存分析结果

        Args:
            results: 分析结果
            output_file: 输出文件路径

        Returns:
            保存结果
        """
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            logger.info(f"结果已保存到: {output_file}")
            return {"status": "success", "file": output_file}
        except Exception as e:
            logger.error(f"保存失败: {str(e)}")
            return {"status": "error", "error": str(e)}


# 全局应用实例
app_instance = None


def get_app() -> NewsAnalysisApp:
    """获取应用实例"""
    global app_instance
    if app_instance is None:
        app_instance = NewsAnalysisApp()
    return app_instance


@click.group()
def cli():
    """新闻分析系统 CLI"""
    pass


@cli.command()
@click.option("--title", "-t", required=True, help="新闻标题")
@click.option("--content", "-c", required=True, help="新闻内容")
@click.option("--workflow", "-w", default="full_analysis", help="工作流名称")
@click.option("--output", "-o", help="输出文件路径")
def analyze(title: str, content: str, workflow: str, output: Optional[str]):
    """分析单篇新闻"""
    click.echo(f"📰 开始分析新闻: {title}")
    click.echo(f"📊 使用工作流: {workflow}")

    app = get_app()

    try:
        result = asyncio.run(app.analyze_news(title, content, workflow))

        if result["status"] == "success":
            click.echo("\n✅ 分析完成!\n")
            click.echo(json.dumps(result["analysis"], ensure_ascii=False, indent=2))

            if output:
                app.save_results(result, output)
                click.echo(f"\n💾 结果已保存到: {output}")
        else:
            click.echo(f"\n❌ 分析失败: {result.get('error')}")
    except Exception as e:
        click.echo(f"\n❌ 错误: {str(e)}")


@cli.command()
@click.option("--file", "-f", required=True, help="输入文件路径 (JSON格式)")
@click.option("--workflow", "-w", default="full_analysis", help="工作流名称")
@click.option("--output", "-o", help="输出文件路径")
def analyze_file(file: str, workflow: str, output: Optional[str]):
    """从文件分析新闻"""
    click.echo(f"📂 从文件读取新闻: {file}")
    click.echo(f"📊 使用工作流: {workflow}")

    app = get_app()

    try:
        result = asyncio.run(app.analyze_file(file, workflow))

        if result["status"] == "success":
            if "total" in result:
                click.echo(f"\n✅ 批量分析完成! 共处理 {result['total']} 篇新闻")
                for idx, item_result in enumerate(result["results"], 1):
                    if item_result.get("status") == "success":
                        click.echo(f"  {idx}. ✓ {item_result['title']}")
                    else:
                        click.echo(f"  {idx}. ✗ 分析失败")
            else:
                click.echo("\n✅ 分析完成!")
                click.echo(json.dumps(result["analysis"], ensure_ascii=False, indent=2))

            if output:
                app.save_results(result, output)
                click.echo(f"\n💾 结果已保存到: {output}")
        else:
            click.echo(f"\n❌ 分析失败: {result.get('error')}")
    except Exception as e:
        click.echo(f"\n❌ 错误: {str(e)}")


@cli.command()
@click.option("--input", "-i", required=True, help="输入文件路径 (JSON格式)")
@click.option("--workflow", "-w", default="full_analysis", help="工作流名称")
@click.option("--output", "-o", required=True, help="输出文件路径")
def batch_analyze(input: str, workflow: str, output: str):
    """批量分析新闻"""
    click.echo(f"📂 从文件读取新闻列表: {input}")
    click.echo(f"📊 使用工作流: {workflow}")

    app = get_app()

    try:
        with open(input, "r", encoding="utf-8") as f:
            news_list = json.load(f)

        if not isinstance(news_list, list):
            click.echo("❌ 错误: 输入文件应为JSON数组格式")
            return

        with click.progressbar(
            length=len(news_list),
            label="处理进度",
        ) as bar:
            result = asyncio.run(app.analyze_batch(news_list, workflow))
            bar.update(len(news_list))

        if result["status"] == "success":
            click.echo(f"\n✅ 批量分析完成! 共处理 {result['total']} 篇新闻")

            # 统计结果
            successful = sum(1 for r in result["results"] if r.get("status") == "success")
            failed = result["total"] - successful
            click.echo(f"   成功: {successful}, 失败: {failed}")

            app.save_results(result, output)
            click.echo(f"\n💾 结果已保存到: {output}")
        else:
            click.echo(f"\n❌ 分析失败: {result.get('error')}")
    except FileNotFoundError:
        click.echo(f"❌ 错误: 文件不存在 {input}")
    except json.JSONDecodeError:
        click.echo("❌ 错误: JSON 格式错误")
    except Exception as e:
        click.echo(f"❌ 错误: {str(e)}")


@cli.command()
def workflows():
    """列出可用的工作流"""
    click.echo("📋 可用的工作流列表:\n")

    app = get_app()
    result = app.get_workflows()

    if result["status"] == "success":
        for workflow_name, info in result["workflows"].items():
            click.echo(f"  📌 {workflow_name}")
            click.echo(f"     模式: {info['mode']}")
            click.echo(f"     任务数: {len(info['tasks'])}")
            for task in info["tasks"]:
                click.echo(f"       - {task['id']} ({task['agent']}.{task['action']})")
            click.echo()
    else:
        click.echo("❌ 获取工作流列表失败")


@cli.command()
def info():
    """显示系统信息"""
    click.echo("ℹ️  系统信息:\n")

    app = get_app()
    result = app.get_system_info()

    if result["status"] == "success":
        info = result["info"]
        click.echo(f"  📦 已注册的Agent:")
        for agent in info["agents"]:
            click.echo(f"     - {agent}")
        click.echo()
        click.echo(f"  📋 已定义的工作流:")
        for workflow in info["workflows"]:
            click.echo(f"     - {workflow}")
        click.echo()
        click.echo(f"  ⚙️  默认工作流:")
        for workflow in info["default_workflows"]:
            click.echo(f"     - {workflow}")
    else:
        click.echo("❌ 获取系统信息失败")


@cli.command()
def version():
    """显示版本信息"""
    click.echo("📊 新闻分析系统 v1.0.0")
    click.echo("   基于多Agent架构的新闻智能分析平台")


@cli.command()
@click.option("--title", "-t", default="示例新闻", help="新闻标题")
@click.option("--content", "-c", default="这是一篇示例新闻内容", help="新闻内容")
def demo(title: str, content: str):
    """运行演示分析"""
    click.echo("🎬 运行演示分析\n")

    app = get_app()

    try:
        click.echo(f"📰 标题: {title}")
        click.echo(f"📄 内容: {content}\n")

        with click.progressbar(length=100, label="分析中") as bar:
            result = asyncio.run(app.analyze_news(title, content, "full_analysis"))
            bar.update(100)

        if result["status"] == "success":
            click.echo("\n✅ 分析完成!\n")
            click.echo("📊 分析结果:")
            click.echo(json.dumps(result["analysis"], ensure_ascii=False, indent=2))
        else:
            click.echo(f"\n❌ 分析失败: {result.get('error')}")
    except Exception as e:
        click.echo(f"\n❌ 错误: {str(e)}")


if __name__ == "__main__":
    cli()
