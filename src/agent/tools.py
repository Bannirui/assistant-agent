TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_ticket",
            "description": "获取工单详情。输入工单ID，返回工单的完整信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string", "description": "工单ID，格式如 TK-20240728-001"}
                },
                "required": ["ticket_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_order",
            "description": "获取订单详情。根据订单ID查询订单的完整信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "订单ID，格式如 ORD-F-001"}
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer",
            "description": "获取客户信息。根据客户ID查询客户档案。",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string", "description": "客户ID，格式如 C10086"}
                },
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_sop",
            "description": "搜索标准操作流程（SOP）。根据产品品类和问题类型查找对应的处理流程、补偿规则和话术模板。",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "产品品类：机票、酒店、火车、打车"},
                    "issue_type": {"type": "string", "description": "问题类型，如：退差价、司机迟到、取消预订等"}
                },
                "required": ["category", "issue_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_refund",
            "description": "计算退改费用。用于需要精确计算的退票、退差价、取消预订等涉及金额的场景。输入订单和客户信息，返回精确的退费金额和计算明细。注意：所有涉及金额的输出必须使用此工具的结果，不得自行计算或估算。",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "产品品类"},
                    "order_id": {"type": "string", "description": "订单ID"},
                    "customer_id": {"type": "string", "description": "客户ID"}
                },
                "required": ["category", "order_id", "customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "搜索公司知识库。当SOP未覆盖当前问题时，使用此工具搜索相关文档、政策、规定。返回最相关的文档片段。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索查询，用自然语言描述要查找的内容"}
                },
                "required": ["query"],
            },
        },
    },
]
