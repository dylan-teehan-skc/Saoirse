import inspect
from dataclasses import dataclass

@dataclass
class Param:
    name: str
    param_type: str
    description: str
    required: bool

    def explode(self):
        return {
            self.name: {
                "type": self.param_type,
                "description": self.description
            }
        }

class Tool:
    def __init__(self, name, description, function):
        self._name = name
        self._description = description
        self._function = function
        self._signature = inspect.signature(function)
        self._sig_parameters = self._signature.parameters
        self._def_params = None

    def get_name(self):
        return self._name
    
    def get_description(self):
        return self._description
    
    def define_function_param(self, list_of_params):
        self._def_params = list_of_params
    
    def export(self):
        if self._def_params is None:
            raise ValueError("Parameters have not been defined. Call define_function_param first.")

        properties = {}
        required = []

        for param in self._def_params:
            properties[param.name] = param.explode()[param.name]
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self._name,
                "description": self._description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
    
    def call(self, *args, **kwargs):
        bound_arguments = self._signature.bind(*args, **kwargs)
        bound_arguments.apply_defaults()
        return self._function(*bound_arguments.args, **bound_arguments.kwargs)