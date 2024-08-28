import os
from textwrap import dedent
from llm_wrap_lib.llm_wrap import DynamicLLMWrapper
from agent_handler.task import Task
from tool_handler.tool import Tool
import logging


class Agent:
    def __init__(self, name, goal, backstory, verbose, json_output=False):
        self._name = name
        self._goal = goal
        self._backstory = backstory
        self._verbose = verbose
        self._json_output = json_output
        self._current_task = None
        self._llm_wrapper = DynamicLLMWrapper()  # Initialize once
        self.tools = []
        self.previous_agent_context = None  # Add this line

    def get_name(self):
        return self._name

    def set_name(self, new_name):
        self._name = new_name

    def add_tool(self, tool: Tool):
        self.tools.append(tool)

    def get_goal(self):
        return self._goal

    def get_task(self):
        return self._current_task

    def set_task(self, new_task_obj):
        self._current_task = new_task_obj

    def set_goal(self, new_goal):
        self._goal = new_goal

    def get_backstory(self):
        return self._backstory

    def set_backstory(self, new_backstory):
        self._backstory = new_backstory

    def get_verbose(self):
        return self._verbose
    
    def set_verbose(self, new_verbose):
        self._verbose = new_verbose
        
    def get_json_output(self):
        return self._json_output

    def set_json_output(self, json_output):
        self._json_output = json_output

    def set_previous_agent_context(self, context):
        logging.debug(f"Setting previous agent context for {self.get_name()}: {context[:100]}...")  # Log first 100 chars
        self.previous_agent_context = context
        self.write_context_to_file(context)

    def read_prompt_from_file(self, file_path):
        with open(file_path, 'r') as file:
            return file.read().strip()
        

    def write_response_to_file(self, description, expected_output, response):
            response_content = dedent(f"""
            <user>
                Agent: {self.get_name()}
                description of task: {description}
                Expected Output: {expected_output}
            </user>
            <ai_response>
                Response: {response.get_response_content()}
                Cost for response: {response.get_cost()}
            </ai_response>
            """)
            with open('response.txt', 'a', encoding='utf-8') as file:
                file.write(response_content)
    def write_context_to_file(self, context):
        with open('context.txt', 'a', encoding='utf-8') as file:
            file.write(f"Context for {self.get_name()}:\n{context}\n\n")
        logging.debug(f"Wrote context to file for {self.get_name()}")

    def execute_task(self):
        if self._current_task is None:
            raise ValueError("No task is set for the agent")
        
        logging.debug(f"Executing task for {self.get_name()}")
        
        tools = [tool.export() for tool in self.tools]
        script_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_file = os.path.join(script_dir, "prompt.txt")

        prompt_template = self.read_prompt_from_file(prompt_file)

        
        description = self._current_task.get_description()
        expected_output = self._current_task.get_expected_output()

        formatted_prompt = prompt_template.format(
            description=description,
            expected_output=expected_output,
            agent_name=self.get_name(),
            agent_goal=self.get_goal(),
            agent_backstory=self.get_backstory(),
            previous_agent_context=self.previous_agent_context
        )
        logging.debug(f"Formatted prompt for {self.get_name()}: {formatted_prompt[:100]}...")  # Log first 100 chars

        self.write_context_to_file(formatted_prompt) 

        if self._json_output:
            formatted_prompt += "\nPlease provide your response in JSON format."
        
        response = self._llm_wrapper.call_model(formatted_prompt, tools=tools)
        logging.debug(f"Response received for {self.get_name()}: {response.get_response_content()[:100]}...")  # Log first 100 chars

        self.write_response_to_file(description, expected_output, response)

        return response.get_response_content()
