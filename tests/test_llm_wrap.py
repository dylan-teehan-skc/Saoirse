import pytest
from unittest.mock import patch, MagicMock
from src.llm_wrap_lib.llm_wrap import DynamicLLMWrapper

@pytest.fixture
def wrapper():
    return DynamicLLMWrapper()

def test_default_model_setter(wrapper):
    wrapper.available_models = {'gpt-3.5-turbo': 'gpt-3.5-turbo', 'gpt-4': 'gpt-4'}
    wrapper.default_model = 'gpt-4'
    assert wrapper.default_model == 'gpt-4'

    with pytest.raises(ValueError):
        wrapper.default_model = 'nonexistent-model'

def test_call_model(wrapper):
    mock_response = MagicMock()
    mock_response.response_cost = 0.02
    mock_response.choices = [MagicMock(message=MagicMock(content="Hello!"))]

    with patch('src.llm_wrap_lib.llm_wrap.litellm.completion', return_value=mock_response):
        wrapper.available_models = {'gpt-3.5-turbo': 'gpt-3.5-turbo'}
        wrapper.default_model = 'gpt-3.5-turbo'

        result = wrapper.call_model("Hi there!")
        assert result['content'] == "Hello!"
        assert result['cost'] == 0.02
        assert wrapper.model_costs['gpt-3.5-turbo'] == 0.02
        assert wrapper.total_cost == 0.02

        # Test with specific model
        result = wrapper.call_model("How are you?", model_name="gpt-3.5-turbo")
        assert wrapper.model_costs['gpt-3.5-turbo'] == 0.04
        assert wrapper.total_cost == 0.04

        # Test with nonexistent model
        with pytest.raises(ValueError):
            wrapper.call_model("Test", model_name="nonexistent-model")

def test_add_custom_model(wrapper):
    wrapper.add_custom_model("custom-model", "path/to/custom/model")
    assert "custom-model" in wrapper.available_models

def test_get_cost_summary(wrapper):
    wrapper.model_costs = {'gpt-3.5-turbo': 0.05, 'gpt-4': 0.1, 'unused-model': 0}
    wrapper.total_cost = 0.15

    summary = wrapper.get_cost_summary()
    assert summary['model_costs'] == {'gpt-3.5-turbo': 0.05, 'gpt-4': 0.1}
    assert summary['total_cost'] == 0.15
    assert 'unused-model' not in summary['model_costs']

def test_reset_costs(wrapper):
    wrapper.model_costs = {'gpt-3.5-turbo': 0.05, 'gpt-4': 0.1}
    wrapper.total_cost = 0.15

    wrapper.reset_costs()
    assert wrapper.model_costs == {}
    assert wrapper.total_cost == 0.0