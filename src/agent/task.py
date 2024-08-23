class Task:
    def __init__(self, description, agent, expected_output, output_json=False):
        self._description = description
        self._agent = agent
        self._expected_output = expected_output
        self._output_json = output_json

    def get_description(self):
        return self._description

    def set_description(self, new_description):
        self._description = new_description

    def get_agent(self):
        return self._agent

    def set_agent(self, new_agent):
        self._agent = new_agent

    def get_expected_output(self):
        return self._expected_output

    def set_expected_output(self, new_expected_output):
        self._expected_output = new_expected_output

    def is_output_json(self):
        return self._output_json

    def set_output_json(self, new_output_json):
        self._output_json = new_output_json