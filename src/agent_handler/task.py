class Task:
    def __init__(self, description: str, expected_output: str, output_json: bool = False) -> None:
        self._description = description
        self._expected_output = expected_output
        self._output_json = output_json

    def get_description(self) -> str:
        return self._description

    def set_description(self, new_description: str) -> None:
        self._description = new_description
 
    def get_expected_output(self) -> str:
        return self._expected_output

    def set_expected_output(self, new_expected_output: str) -> None:
        self._expected_output = new_expected_output

    def is_output_json(self) -> bool:
        return self._output_json

    def set_output_json(self, new_output_json: bool) -> None:
        self._output_json = new_output_json