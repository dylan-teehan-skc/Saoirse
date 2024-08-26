from typing import Dict, List, Callable
from agent_handler.agent import Agent

class State(Agent):
    def __init__(self, agent: Agent):
        super().__init__(name=agent.get_name(), goal=agent.get_goal(), backstory=agent.get_backstory(), verbose=agent.get_verbose())
        self._current_task = agent.get_task()  # Transfer the task from the agent to the state
        self.action = self.execute_task
        self.agent = agent  # Keep a reference to the original agent

    def execute_task(self):
        if self._current_task is None:
            print(f"No task is set for the agent {self.get_name()}. Skipping execution.")
            return
        return super().execute_task()

    def get_agent(self):
        return self.agent

  


class Transition:
    def __init__(self, target_state: State, condition: Callable[[], bool] = lambda: True):
        self.target_state = target_state
        self.condition = condition

class StateMachine:
    def __init__(self):
        self.states: Dict[State, List[Transition]] = {}
        self.current_state: State = None

    def add_state(self, state: State) -> None:
        if state not in self.states:
            self.states[state] = []

    def add_transition(self, from_state: State, to_state: State, condition: Callable[[], bool] = lambda: True) -> None:
        if from_state not in self.states or to_state not in self.states:
            raise ValueError("Both states must exist before adding a transition")
        transition = Transition(to_state, condition)
        self.states[from_state].append(transition)

    def set_initial_state(self, state: State) -> None:
        if state not in self.states:
            raise ValueError("Initial state must exist")
        self.current_state = state

    def run(self) -> None:
        while self.current_state:
            print(f"Current state: {self.current_state.get_name()}")
            self.current_state.action()
            next_state = None
            for transition in self.states[self.current_state]:
                if transition.condition():
                    next_state = transition.target_state
                    break
            if next_state:
                self.current_state = next_state
            else:
                print(f"No valid transition from {self.current_state.get_name()}. Ending execution.")
                break

    def to_dict(self):
        return {
            "states": [state.get_name() for state in self.states],
            "transitions": [
                {
                    "from": from_state.get_name(),
                    "to": transition.target_state.get_name()
                }
                for from_state, transitions in self.states.items()
                for transition in transitions
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict, agents: Dict[str, Agent]):
        sm = cls()
        for state_name in data["states"]:
            sm.add_state(State(agents[state_name]))
        for transition in data["transitions"]:
            from_state = next(state for state in sm.states if state.get_name() == transition["from"])
            to_state = next(state for state in sm.states if state.get_name() == transition["to"])
            sm.add_transition(from_state, to_state)
        return sm