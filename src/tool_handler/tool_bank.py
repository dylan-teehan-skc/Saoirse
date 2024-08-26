from tool_handler.tool import Tool, Param
from typing import Dict, List, Optional

class ToolBank:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ToolBank, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'tools'):
            self.tools: Dict[str, Tool] = {}

    def add_tool(self, tool: Tool) -> None:
        self.tools[tool.get_name()] = tool

    def add_tools(self, tools: List[Tool]) -> None:
        for tool in tools:
            self.add_tool(tool)

    def get_tool(self, tool_name: str) -> Optional[Tool]:
        return self.tools.get(tool_name, None)

    def get_all_tools(self) -> Dict[str, Tool]:
        return self.tools

