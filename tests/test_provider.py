import pytest
from unittest.mock import patch, MagicMock
from src.llm.providers.openai import OpenAICompatibleProvider
from src.llm.provider import ProviderRegistry


class TestOpenAICompatibleProvider:
    @pytest.fixture
    def provider(self):
        return OpenAICompatibleProvider(
            base_url="https://test.api.com/v1",
            api_key="test-key",
            model="test-model",
        )

    def test_chat_returns_response(self, provider):
        with patch.object(provider, "_get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            mock_choice = MagicMock()
            mock_choice.message.content = "Hello"
            mock_choice.message.tool_calls = None
            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_client.chat.completions.create.return_value = mock_response

            result = provider.chat(
                messages=[{"role": "user", "content": "Hi"}],
            )

            assert result.content == "Hello"
            assert result.tool_calls is None

    def test_chat_with_tools(self, provider):
        with patch.object(provider, "_get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            mock_tc = MagicMock()
            mock_tc.id = "call_123"
            mock_tc.type = "function"
            mock_tc.function.name = "get_weather"
            mock_tc.function.arguments = '{"city": "Beijing"}'

            mock_choice = MagicMock()
            mock_choice.message.content = None
            mock_choice.message.tool_calls = [mock_tc]
            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_client.chat.completions.create.return_value = mock_response

            result = provider.chat(
                messages=[{"role": "user", "content": "Weather?"}],
                tools=[{"type": "function", "function": {"name": "get_weather"}}],
            )

            assert result.content is None
            assert len(result.tool_calls) == 1
            assert result.tool_calls[0]["id"] == "call_123"
            assert result.tool_calls[0]["function"]["name"] == "get_weather"

    def test_embed_returns_vectors(self, provider):
        with patch.object(provider, "_get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            mock_data = [MagicMock(), MagicMock()]
            mock_data[0].embedding = [0.1, 0.2, 0.3]
            mock_data[1].embedding = [0.4, 0.5, 0.6]
            mock_response = MagicMock()
            mock_response.data = mock_data
            mock_client.embeddings.create.return_value = mock_response

            result = provider.embed(["text1", "text2"])

            assert len(result) == 2
            assert result[0] == [0.1, 0.2, 0.3]
            assert result[1] == [0.4, 0.5, 0.6]


class TestProviderRegistry:
    def test_register_and_get_chat(self):
        registry = ProviderRegistry()
        provider = OpenAICompatibleProvider(
            base_url="https://chat.test.com",
            api_key="k1",
            model="m1",
        )
        registry.register_chat(provider)
        assert registry.chat is provider

    def test_register_and_get_embed(self):
        registry = ProviderRegistry()
        provider = OpenAICompatibleProvider(
            base_url="https://embed.test.com",
            api_key="k2",
            model="m2",
        )
        registry.register_embed(provider)
        assert registry.embed is provider

    def test_get_chat_not_registered(self):
        registry = ProviderRegistry()
        with pytest.raises(RuntimeError, match="Chat provider not registered"):
            _ = registry.chat

    def test_get_embed_not_registered(self):
        registry = ProviderRegistry()
        with pytest.raises(RuntimeError, match="Embedding provider not registered"):
            _ = registry.embed

    def test_registry_initial_state(self):
        from src.llm.provider import ProviderRegistry
        registry = ProviderRegistry()
        assert registry._chat_provider is None
        assert registry._embed_provider is None
