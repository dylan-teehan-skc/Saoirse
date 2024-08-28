import pytest
from src.llm_wrap_lib.llm_wrap import DynamicLLMWrapper
import os

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
    # Ensure mocking is enabled
    wrapper.config['mocking'] = True
    wrapper.save_config()

    wrapper.available_models = {'gpt-3.5-turbo': 'gpt-3.5-turbo'}
    wrapper.default_model = 'gpt-3.5-turbo'

    result = wrapper.call_model("Hi there!")
    assert "Mocked response for prompt: Hi there!" in result.get_response_content()
    assert float(result.get_cost()) == 0.0001
    assert wrapper.model_costs['gpt-3.5-turbo'] == 0.0001
    assert wrapper.total_cost == 0.0001

    # Test with specific model
    result = wrapper.call_model("How are you?", model_name="gpt-3.5-turbo")
    assert "Mocked response for prompt: How are you?" in result.get_response_content()
    assert float(result.get_cost()) == 0.0001
    assert wrapper.model_costs['gpt-3.5-turbo'] == 0.0002
    assert wrapper.total_cost == 0.0002

    # Test with nonexistent model
    # try:
    #     wrapper.call_model("Test", model_name="nonexistent-model")
    #     pytest.fail("Expected ValueError was not raised")
    # except ValueError as e:
    #     assert str(e) == "Model nonexistent-model is not available"

def test_add_custom_model(wrapper):
    wrapper.add_custom_model("custom-model", "path/to/custom/model")
    assert "custom-model" in wrapper.available_models

def test_get_cost_summary(wrapper):
    wrapper.model_costs = {'gpt-3.5-turbo': 0.0001, 'gpt-4': 0.0002, 'unused-model': 0}
    wrapper.total_cost = 0.0003

    summary = wrapper.get_cost_summary()
    assert summary['model_costs'] == {'gpt-3.5-turbo': 0.0001, 'gpt-4': 0.0002}
    assert summary['total_cost'] == 0.0003
    assert 'unused-model' not in summary['model_costs']

def test_reset_costs(wrapper):
    wrapper.model_costs = {'gpt-3.5-turbo': 0.0001, 'gpt-4': 0.0002}
    wrapper.total_cost = 0.0003

    wrapper.reset_costs()
    assert wrapper.model_costs == {}
    assert wrapper.total_cost == 0.0

def test_mocking_enabled(wrapper):
    # Ensure mocking is enabled
    wrapper.config['mocking'] = True
    wrapper.save_config()

    result = wrapper.call_model("Test prompt")
    assert "Mocked response for prompt: Test prompt" in result.get_response_content()
    assert float(result.get_cost()) == 0.0001

def test_mocking_disabled(wrapper):
    # Disable mocking
    wrapper.config['mocking'] = False
    wrapper.save_config()

    # Check if the API key is set
    api_key = os.environ.get('OPENAI_API_KEY')
    assert api_key is not None, "API_KEY is not set in the environment"

    # Set the API key for the OpenAI client
    import openai
    openai.api_key = api_key

    # Rest of your test...
    result = wrapper.call_model("Test prompt")
    assert "Mocked response for prompt: Test prompt" not in result.get_response_content()