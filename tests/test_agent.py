import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture(autouse=True)
def setup_sops():
    from src.sop.engine import sop_engine
    sop_engine.load_all()



@pytest.fixture
def mock_openai():
    with patch("src.agent.copilot_agent.OpenAI") as mock:
        client = MagicMock()
        mock.return_value = client

        response = MagicMock()
        choice = MagicMock()
        msg = MagicMock()
        msg.content = """{
  "analysis": {
    "intent": "退差价投诉",
    "emotion": "愤怒",
    "risk": "高 - 客户威胁12315投诉"
  },
  "reply_template": "您好张三先生，非常抱歉给您带来不好的体验...",
  "suggested_actions": [
    {"type": "refund", "label": "发起退款 ¥234"},
    {"type": "escalate", "label": "升级主管"}
  ],
  "references": {
    "order_summary": "CA1234 | Y舱 | ¥1560",
    "customer_info": "张三 | 金卡会员",
    "policy_excerpt": "价格保护政策..."
  },
  "warnings": ["客户情绪激动，请优先安抚"]
}"""
        msg.tool_calls = None
        choice.message = msg
        response.choices = [choice]
        client.chat.completions.create.return_value = response

        yield mock


class TestAgentToolExecution:
    def test_get_ticket_tool(self):
        from src.agent.copilot_agent import agent
        result = agent._execute_tool("get_ticket", {"ticket_id": "TK-20240728-001"})
        assert "TK-20240728-001" in result
        assert "退差价" in result

    def test_get_ticket_not_found(self):
        from src.agent.copilot_agent import agent
        result = agent._execute_tool("get_ticket", {"ticket_id": "TK-NOT-EXIST"})
        assert result == "工单未找到"

    def test_get_order_tool(self):
        from src.agent.copilot_agent import agent
        result = agent._execute_tool("get_order", {"order_id": "ORD-F-001"})
        assert "CA1234" in result

    def test_get_order_not_found(self):
        from src.agent.copilot_agent import agent
        result = agent._execute_tool("get_order", {"order_id": "ORD-NOT-EXIST"})
        assert result == "订单未找到"

    def test_get_customer_tool(self):
        from src.agent.copilot_agent import agent
        result = agent._execute_tool("get_customer", {"customer_id": "C10086"})
        assert "张三" in result
        assert "gold" in result

    def test_search_sop_tool_match(self):
        from src.agent.copilot_agent import agent
        result = agent._execute_tool("search_sop", {"category": "打车", "issue_type": "司机迟到"})
        assert "RIDE_DRIVER_LATE" in result

    def test_search_sop_tool_no_match(self):
        from src.agent.copilot_agent import agent
        result = agent._execute_tool("search_sop", {"category": "游轮", "issue_type": "退票"})
        assert result == "未匹配到SOP"

    def test_calculate_refund_tool(self):
        from src.agent.copilot_agent import agent
        result = agent._execute_tool(
            "calculate_refund",
            {"category": "机票", "order_id": "ORD-F-001", "customer_id": "C10086"},
        )
        assert "refundable" in result

    def test_calculate_refund_missing_data(self):
        from src.agent.copilot_agent import agent
        result = agent._execute_tool(
            "calculate_refund",
            {"category": "机票", "order_id": "ORD-NOT-EXIST", "customer_id": "C10086"},
        )
        assert "无法计算" in result


class TestOutputParser:
    def test_parse_valid_json(self):
        from src.agent.copilot_agent import agent
        content = """Some text before
{
  "analysis": {"intent": "test"},
  "reply_template": "hello",
  "suggested_actions": [],
  "references": {},
  "warnings": []
}
Some text after"""
        result = agent._parse_output(content)
        assert result["analysis"]["intent"] == "test"
        assert result["reply_template"] == "hello"

    def test_parse_invalid_content(self):
        from src.agent.copilot_agent import agent
        result = agent._parse_output("just plain text, no json here")
        assert result["analysis"]["intent"] == "解析失败"
