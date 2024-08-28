from typing import Dict, List, Callable
from agent_handler.agent import Agent
from PySide6.QtCore import QObject, Signal, QMetaObject, Qt, Slot, Q_ARG

class State:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.action = self.execute_task
        self.connections = []
        self.context = None
        self.response = None

    def execute_task(self, context=None):
        self.context = context
        if context:
            self.agent.set_previous_agent_context(context)
        self.response = self.agent.execute_task()
        return self.response

    def add_connection(self, to_state: 'State'):
        self.connections.append(to_state)

    def get_name(self):
        return self.agent.get_name()

    def get_agent(self):
        return self.agent

    def get_response(self):
        return self.response

    def get_next_state(self):
        return self.connections[0] if self.connections else None

class StateWrapper(QObject):
    response_ready = Signal(str)

    def __init__(self, state: State):
        super().__init__()
        self._state = state

    def get_state(self) -> State:
        return self._state

    @Slot(str)
    def update_response(self, response: str):
        self._state.response = response
        self.response_ready.emit(response)

class StateMachine(QObject):
    state_changed = Signal(StateWrapper)
    execution_finished = Signal()

    def __init__(self):
        super().__init__()
        self.states = []
        self.current_state = None
        self.context_passing = {}

    def run(self):
        context = None
        while self.current_state:
            print(f"Executing state: {self.current_state.get_name()}")
            wrapper = StateWrapper(self.current_state)
            self.emitStateChanged(wrapper)
            result = self.current_state.execute_task(context)
            wrapper.update_response(result)
            next_state = self.current_state.get_next_state()
            if next_state:
                if self.should_pass_context(self.current_state.get_name(), next_state.get_name()):
                    context = f"{self.current_state.get_name()} Response: {result}"
                    next_state.agent.set_previous_agent_context(context)
                else:
                    context = None
                    next_state.agent.set_previous_agent_context(None)
                self.current_state = next_state
            else:
                print(f"Final state reached. Execution complete.")
                self.emitExecutionFinished()
                break

    def should_pass_context(self, from_state_name, to_state_name):
        return self.context_passing.get(from_state_name, {}).get(to_state_name, False)

    def set_context_passing(self, from_state_name, to_state_name, should_pass):
        if from_state_name not in self.context_passing:
            self.context_passing[from_state_name] = {}
        self.context_passing[from_state_name][to_state_name] = should_pass

    @Slot(StateWrapper)
    def emitStateChanged(self, state_wrapper):
        self.state_changed.emit(state_wrapper)

    @Slot()
    def emitExecutionFinished(self):
        self.execution_finished.emit()

    def add_state(self, state: State):
        self.states.append(state)

    def add_transition(self, from_state: State, to_state: State):
        from_state.add_connection(to_state)

    def set_initial_state(self, state: State):
        if state not in self.states:
            raise ValueError("Initial state must exist in the state machine")
        self.current_state = state

    def to_dict(self):
        return {
            "states": [
                {
                    "name": state.agent.get_name(),
                    "x": state.x if hasattr(state, 'x') else 0,
                    "y": state.y if hasattr(state, 'y') else 0,
                    "connections": [
                        {"to": conn.get_name()}
                        for conn in state.connections
                    ]
                }
                for state in self.states
            ],
            "context_passing": self.context_passing
        }

    @classmethod
    def from_dict(cls, data: Dict, agents: Dict[str, Agent]):
        sm = cls()
        states = {}
        for state_data in data["states"]:
            agent = agents[state_data["name"]]
            state = State(agent)
            state.x = state_data.get("x", 0)
            state.y = state_data.get("y", 0)
            states[state_data["name"]] = state
            sm.add_state(state)

        for state_data in data["states"]:
            state = states[state_data["name"]]
            for conn in state_data.get("connections", []):
                to_state = states[conn["to"]]
                sm.add_transition(state, to_state)

        sm.context_passing = data.get("context_passing", {})
        return sm