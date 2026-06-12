# 🗞️ 新闻分析与摘要系统

基于DeepSeek大模型的智能新闻分析与摘要系统，采用Multi-Agent架构，集成RAG知识库、LangChain框架，实现新闻采集、智能分析、实时展示的完整解决方案。

## 📊 系统架构

```
新闻采集 → 数据预处理 → 向量化存储(Chroma) → Multi-Agent分析 → 结果展示
   ↓          ↓            ↓              ↓           ↓
  RSS/API   清洗去重    向量嵌入      6个专业Agent    Web/API
```

## ✨ 核心功能

### 1. **智能摘要** (Summary Agent)
- 一句话摘要生成
- 详细摘要提取
- 关键信息突出

### 2. **内容分类** (Classify Agent)
- 自动分类新闻
- 置信度评分
- 支持自定义分类

### 3. **情感分析** (Sentiment Agent)
- 正面/负面/中立判断
- 情感指数量化
- 趋势分析

### 4. **关键词提取** (Keyword Agent)
- 权重关键词识别
- 实体识别
- 主题聚类

### 5. **热点评估** (Hotspot Agent)
- 新闻热度计算
- 相似度检测
- 趋势预测

### 6. **信息校验** (Verify Agent)
- 虚假信息检测
- 来源可信度评分
- 事实核查

## 🛠️ 技术栈

| 组件 | 技术 | 说明 |
|------|-----|------|
| 大模型 | DeepSeek | 国产高性能模型 |
| 框架 | LangChain | Agent编排与工具链 |
| 向量库 | Chroma | 本地向量存储 |
| 后端 | FastAPI | 高性能RESTful API |
| 前端 | Streamlit | 快速数据应用开发 |
| 数据库 | SQLite + Chroma | 元数据与向量存储 |
| 爬虫 | Feedparser | RSS新闻源采集 |

## 📁 项目结构

```
news-analysis-system/
├── README.md
├── requirements.txt
├── config.yaml
├── .env.example
│
├── src/
│   ├── config/
│   │   ├── settings.py          # 全局配置
│   │   └── prompts.py           # DeepSeek提示词库
│   │
│   ├── data/
│   │   ├── fetcher.py           # 新闻采集
│   │   ├── processor.py         # 数据预处理
│   │   └── storage.py           # 数据存储
│   │
│   ├── rag/
│   │   ├── vectorstore.py       # Chroma向量库
│   │   ├── embeddings.py        # 向量化
│   │   └── retriever.py         # 检索器
│   │
│   ├── agents/
│   │   ├── base_agent.py        # 基础Agent
│   │   ├── summary_agent.py     # 摘要Agent
│   │   ├── classify_agent.py    # 分类Agent
│   │   ├── sentiment_agent.py   # 情感Agent
│   │   ├── keyword_agent.py     # 关键词Agent
│   │   ├── hotspot_agent.py     # 热点Agent
│   │   ├── verify_agent.py      # 校验Agent
│   │   └── coordinator.py       # Agent协调器
│   │
│   ├── tools/
│   │   ├── search_tools.py      # 搜索工具
│   │   ├── verify_tools.py      # 验证工具
│   │   └── trend_tools.py       # 趋势工具
│   │
│   ├── api/
│   │   ├── main.py              # FastAPI应用
│   │   ├── routes.py            # API路由
│   │   └── schemas.py           # 数据模型
│   │
│   └── web/
│       └── app.py               # Streamlit应用
│
├── tests/
│   ├── test_agents.py
│   ├── test_rag.py
│   └── test_api.py
│
├── data/
│   ├── raw_news/
│   ├── chroma_db/
│   └── news.db
│
└── docs/
    ├── design.md                # 设计文档
    ├── api_spec.md              # API规范
    └── report.md                # 课程报告
```

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/zxdsv/news-analysis-system.git
cd news-analysis-system
```

### 2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env，添加 DeepSeek API 密钥
DEEPSEEK_API_KEY=your_key_here
```

### 5. 初始化数据库
```bash
python -m src.data.storage init
```

### 6. 启动应用

**选项A：Web界面**
```bash
streamlit run src/web/app.py
```

**选项B：API服务**
```bash
python src/api/main.py
```

## 📚 使用示例

### Python调用
```python
from src.agents.coordinator import NewsAnalysisCoordinator

coordinator = NewsAnalysisCoordinator()

# 分析单条新闻
result = coordinator.analyze_news(
    title="新标题",
    content="新闻内容...",
)

print(f"摘要: {result['summary']}")
print(f"分类: {result['category']}")
print(f"情感: {result['sentiment']}")
```

### API调用
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "title": "新标题",
    "content": "新闻内容..."
  }'
```

## 🧪 测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_agents.py -v
```

## 📊 性能指标

- **摘要生成**: ~2-3秒/条
- **多Agent分析**: ~5-8秒/条
- **向量检索**: <100ms
- **API吞吐量**: >100 req/s

## 🔑 关键特性

✅ **Multi-Agent架构** - 6个专业Agent协作分析
✅ **RAG知识库** - 上下文感知增强
✅ **Tool Calling** - 函数调用支持
✅ **向量化存储** - Chroma高效检索
✅ **实时更新** - 定时新闻抓取
✅ **可视化展示** - Web界面与API
✅ **可扩展设计** - 易于添加新Agent

## 📖 文档

- [系统设计文档](docs/design.md)
- [API规范](docs/api_spec.md)
- [课程设计报告](docs/report.md)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 👨‍💼 作者

zxdsv

---

**课程设计项目 | 基于DeepSeek的大模型应用** 🎓
