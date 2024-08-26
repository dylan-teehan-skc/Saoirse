from typing import List, Dict
import litellm
from litellm.utils import get_valid_models
import json
from tool_handler.tool_bank import ToolBank

class Response:
    def __init__(self, response_dict: Dict[str, any]):
        self._content = response_dict.get('content', '')
        self._cost = response_dict.get('cost', 0.0)

    def get_response_content(self) -> str:
        """Return the content of the LLM response."""
        return self._content if self._content is not None else ""
    
    def get_cost(self) -> float:
        """Return the cost of the LLM call."""
        return self._cost

    def __str__(self) -> str:
        """Return the response content when the object is cast to a string."""
        return self.get_response_content()
    

class DynamicLLMWrapper:
    def __init__(self):
        self.available_models: Dict[str, str] = {}
        self._default_model: str = None
        self.model_costs: Dict[str, float] = {}
        self.total_cost: float = 0.0
        self.initialize_models()

    def initialize_models(self):
        valid_models = get_valid_models()
        
        for model in valid_models:
            self.available_models[model] = model
        
        # Set the default model to the first available model
        if valid_models and self._default_model is None:
            self._default_model = valid_models[0]

    @property
    def default_model(self) -> str:
        return self._default_model

    @default_model.setter
    def default_model(self, model: str):
        if model not in self.available_models:
            raise ValueError(f"Model {model} is not available")
        self._default_model = model

    def get_available_models(self) -> List[str]:
        return list(self.available_models.keys())

    def _update_return_costs(self, response, model_name: str):
        cost = response._hidden_params["response_cost"]
        if model_name not in self.model_costs:
            self.model_costs[model_name] = 0.0

        self.model_costs[model_name] += cost
        self.total_cost += cost

        return format(cost, '.4f')
        
    def call_model(self, prompt: str, model_name: str = None, tools: list = None, **kwargs) -> Response:
        if model_name is None:
            model_name = self.default_model
        if model_name not in self.available_models:
            raise ValueError(f"Model {model_name} is not available")

        messages = [{"role": "user", "content": prompt}]
        
        while True:
            response = litellm.completion(model=model_name, messages=messages, tools=tools, **kwargs)
            
            tool_calls = response.choices[0].message.tool_calls
            
            if not tool_calls:
                # If there are no tool calls, we have our final response
                break
            
            # Process tool calls
            messages.append({"role": "assistant", "content": response.choices[0].message.content, "tool_calls": tool_calls})
            
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_params = json.loads(tool_call.function.arguments)
                tool = ToolBank().get_tool(tool_name)  # assuming ToolBank is a singleton
                tool_response = tool.call(**tool_params)
                messages.append({"role": "tool", "content": str(tool_response), "tool_call_id": tool_call.id})

        cost = self._update_return_costs(response, model_name)

        return Response({
            "content": response.choices[0].message.content,
            "cost": cost
        })

    def add_custom_model(self, name: str, model_path: str):
        self.available_models[name] = model_path

    def refresh_models(self):
        """Refresh the list of available models"""
        self.initialize_models()

    def get_cost_summary(self) -> Dict[str, float]:
        return {
            "model_costs": {model: cost for model, cost in self.model_costs.items() if cost > 0},
            "total_cost": self.total_cost
        }

    def reset_costs(self):
        """Reset all cost tracking to zero"""
        self.model_costs.clear()
        self.total_cost = 0.0