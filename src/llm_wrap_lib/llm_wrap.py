from typing import List, Dict
import litellm
from litellm.utils import get_valid_models

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

    def call_model(self, prompt: str, model_name: str = None, **kwargs) -> Dict[str, any]:
        if model_name is None:
            model_name = self.default_model
        
        if model_name not in self.available_models:
            raise ValueError(f"Model {model_name} is not available")

        response = litellm.completion(model=model_name, messages=[{"role": "user", "content": prompt}], **kwargs)
        
        # Update costs
        cost = response.response_cost
        if model_name not in self.model_costs:
            self.model_costs[model_name] = 0.0
        self.model_costs[model_name] += cost
        self.total_cost += cost

        return {
            "content": response.choices[0].message.content,
            "cost": cost
        }

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