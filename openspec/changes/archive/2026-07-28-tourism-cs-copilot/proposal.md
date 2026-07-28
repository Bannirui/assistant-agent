## Why

旅游企业客服团队每天处理大量客诉工单，处理一个工单需要客服依次查询多个系统（订单系统、CRM、退改规则库、知识库），信息碎片化导致效率低下。AI Copilot 以工单号为唯一输入，自动聚合所有相关上下文，生成建议回复话术和操作建议，将客服从"信息搬运工"转变为"决策确认者"。

## What Changes

- 新增 **工单分析管线**（ReAct Agent 架构）：输入工单号，自动拉取工单详情，LLM 自主决策需要查询哪些外部系统
- 新增 **多品类订单路由**：根据工单的 product_category（机票/酒店/火车/打车）自动路由到对应 Mock 订单系统
- 新增 **SOP 匹配引擎**：客服组长可维护结构化 SOP 文档（YAML），Agent 按条件匹配标准处理流程和话术模板
- 新增 **退改计算引擎**：机票/酒店等产品的退改费用、差额补偿等涉及金额的确定性计算，LLM 不得自行计算
- 新增 **RAG 知识库检索**：对公司内部文档（Wiki、政策文档）建立向量索引，当 SOP 覆盖不到时兜底检索
- 新增 **Copilot 工作台前端**：左侧对话面板 + 右侧 Copilot 分析面板，展示建议回复、建议操作按钮、风险提示

## Capabilities

### New Capabilities

- `ticket-analysis-pipeline`: 核心分析管线——ReAct Agent 接收工单号，自主决策调用工具链（拉工单、查订单、查用户、查SOP、查知识库、调计算引擎），最终合成回复建议和操作建议
- `order-router`: 多品类订单查询路由——根据工单 `category` 字段（机票/酒店/火车/打车），将 `get_order` 调用路由到对应的 Mock 外部系统
- `sop-engine`: SOP 匹配引擎——结构化 SOP 文档的加载、匹配、返回，支持按 category + issue_type 组合条件匹配
- `refund-calculator`: 退改计算引擎——机票/酒店等产品的确定性退改费用计算，输入订单+用户信息，输出精确金额和操作建议
- `knowledge-rag`: RAG 知识库检索——对公司文档建立向量索引，Agent 通过 `search_knowledge` 工具进行语义检索，作为 SOP 未覆盖场景的兜底方案
- `copilot-workstation`: Copilot 工作台前端——结构化客服工作台，包含对话面板、工单分析面板、建议回复区、操作按钮区、风险提示区

### Modified Capabilities

<!-- No existing capabilities to modify -->

## Impact

- **新增后端服务**: `copilot-service`（FastAPI），包含 Agent 引擎、SOP 引擎、计算引擎、知识库 RAG 模块
- **新增 Mock 服务**: 工单系统、OMS/PMS/CRM/Policy 系统的 Mock API
- **新增前端应用**: `copilot-workstation`（React/Vue），工作台界面
- **新增基础设施**: 向量数据库（如 Qdrant/Chroma）用于 RAG，PostgreSQL 用于业务数据
- **依赖**: OpenAI API（或兼容 LLM API）、向量数据库
