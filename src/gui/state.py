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
        if context and isinstance(context, dict):
            self.agent._current_task.set_description(f"{self.agent._current_task.get_description()}\nContext from previous agent: {context}")
        self.response = self.agent.execute_task()
        return self.response

    def add_connection(self, to_state: 'State', pass_context: bool = False):
        self.connections.append((to_state, pass_context))

    def get_name(self):
        return self.agent.get_name()

    def get_agent(self):
        return self.agent

    def get_response(self):
        return self.response

    def get_next_state(self):
        return self.connections[0][0] if self.connections else None

    def should_pass_context(self):
        return self.connections[0][1] if self.connections else False

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

    def run(self):
        context = None
        while self.current_state:
            print(f"Executing state: {self.current_state.agent.get_name()}")
            wrapper = StateWrapper(self.current_state)
            self.emitStateChanged(wrapper)
            result = self.current_state.execute_task(context)
            # Update the response in the wrapper
            wrapper.update_response(result)
            next_state = self.current_state.get_next_state()
            if next_state:
                if self.current_state.should_pass_context():
                    context = {"previous_result": result}
                else:
                    context = None
                self.current_state = next_state
            else:
                print(f"Final state reached. Execution complete.")
                self.emitExecutionFinished()
                break

    @Slot(StateWrapper)
    def emitStateChanged(self, state_wrapper):
        self.state_changed.emit(state_wrapper)

    @Slot()
    def emitExecutionFinished(self):
        self.execution_finished.emit()

    def add_state(self, state: State):
        self.states.append(state)

    def add_transition(self, from_state: State, to_state: State, pass_context: bool = False):
        from_state.add_connection(to_state, pass_context)

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
                        {"to": conn[0].agent.get_name(), "pass_context": conn[1]}
                        for conn in state.connections
                    ]
                }
                for state in self.states
            ]
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
                sm.add_transition(state, to_state, conn["pass_context"])

        return sm

class Connection:
    def __init__(self, from_state: State, to_state: State, pass_context: bool = False):
        self.from_state = from_state
        self.to_state = to_state
        self.pass_context = pass_context



class Transition:
    def __init__(self, target_state: State, condition: Callable[[], bool] = lambda: True):
        self.target_state = target_state
        self.condition = condition

