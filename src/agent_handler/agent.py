from llm_wrap_lib.llm_wrap import DynamicLLMWrapper
from agent_handler.task import Task
import os

class Agent:
    def __init__(self, name, goal, backstory, verbose, task_obj: Task = None):
        self._name = name
        self._goal = goal
        self._backstory = backstory
        self._verbose = verbose
        self._current_task = task_obj

    def get_name(self):
        return self._name

    def set_name(self, new_name):
        self._name = new_name

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
        
    def complete_task(self, output_json = None, task_obj = None):

        if task_obj is None:
            task_obj = self.get_task()
            if task_obj is None:
                raise ValueError("Task object was not provided and no task object is set for the agent")
    
        llm_wrapper = DynamicLLMWrapper() # this should not be initalized everytime, singleton


        script_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_file = os.path.join(script_dir, "prompt.txt") # this could probably do with some work :) future us

        prompt_template = read_prompt_from_file(prompt_file)
        
        description = task_obj.get_description
        expected_output = task_obj.get_expected_output

        # Format the prompt with the provided variables
        formatted_prompt = prompt_template.format(
            description=description,
            expected_output=expected_output,
            agent_name=self.get_name(),
            agent_goal=self.get_goal(),
            agent_backstory=self.get_backstory()
        )
        
        response = llm_wrapper.call_model(formatted_prompt)

        with open('response.txt', 'a', encoding='utf-8') as file:
            file.write(f"{self.get_name()} response: ")
            file.write(f"{response.get_response_content()} \n")
            file.write(f"Cost for response: {str(response.get_cost())}")
            file.write("\n")
            file.write("\n")
            file.write("\n")
            file.write("\n")

def read_prompt_from_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()