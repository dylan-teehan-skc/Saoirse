import json
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, 
    QComboBox, QSplitter, QLabel, QListWidget, QListWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Slot, Signal, QObject
from gui.node_editor import NodeEditor, Connection
from gui.sidebar import Sidebar
from gui.agent_widget import DraggableAgentWidget
from gui.state import StateMachine, StateWrapper

class StateMachineWorker(QObject):
    finished = Signal()
    error = Signal(str)

    def __init__(self, state_machine):
        super().__init__()
        self.state_machine = state_machine

    @Slot()
    def run(self):
        try:
            self.state_machine.run()
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agent-based State Machine Editor")
        self.setGeometry(100, 100, 1000, 600)

        self.agents = {}

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout()
        central_widget.setLayout(layout)

        self.sidebar = Sidebar()
        self.sidebar.toggle_signal.connect(self.toggle_sidebar)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        button_layout = QHBoxLayout()
        content_layout.addLayout(button_layout)

        self.agent_combo = QComboBox()
        button_layout.addWidget(self.agent_combo)

        add_agent_button = QPushButton("Add Agent")
        add_agent_button.clicked.connect(self.add_agent)
        button_layout.addWidget(add_agent_button)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_state_machine)
        button_layout.addWidget(save_button)

        load_button = QPushButton("Load")
        load_button.clicked.connect(self.load_state_machine)
        button_layout.addWidget(load_button)

        run_button = QPushButton("Run State Machine")
        run_button.clicked.connect(self.run_state_machine)
        button_layout.addWidget(run_button)

        self.agents_list = QListWidget()
        self.agents_list.setFlow(QListWidget.LeftToRight)
        self.agents_list.setWrapping(False)
        self.agents_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.agents_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.agents_list.setMaximumHeight(52)
        content_layout.addWidget(QLabel("Draggable Agents:"))
        content_layout.addWidget(self.agents_list)

        self.node_editor = NodeEditor(self.agents)
        content_layout.addWidget(self.node_editor)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(content_widget)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

        self.node_editor.node_clicked.connect(self.update_sidebar_on_click)
        self.node_editor.node_properties_updated.connect(self.update_sidebar_with_context_and_response)

        self.worker = None
        self.thread = None

    def toggle_sidebar(self, show):
        if show:
            self.sidebar.content.show()
        else:
            self.sidebar.content.hide()

    def update_sidebar(self, agent):
        self.sidebar.update_properties(agent)
        if not self.sidebar.content.isVisible():
            self.toggle_sidebar(True)

    def set_agents(self, agents):
        self.agents = agents
        self.agent_combo.clear()
        self.agent_combo.addItems(self.agents.keys())
        self.node_editor.agents = self.agents
        
        self.agents_list.clear()
        for agent_name, agent in self.agents.items():
            item = QListWidgetItem(self.agents_list)
            widget = DraggableAgentWidget(agent)
            item.setSizeHint(widget.sizeHint())
            self.agents_list.addItem(item)
            self.agents_list.setItemWidget(item, widget)

    def add_agent(self):
        selected_agent_name = self.agent_combo.currentText()
        if selected_agent_name in self.agents:
            agent = self.agents[selected_agent_name]
            self.node_editor.addNode(agent, 0, 0)
        else:
            print(f"Agent {selected_agent_name} not found.")

    def save_state_machine(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save State Machine", "", "JSON Files (*.json)")
        if file_name:
            data = self.node_editor.state_machine.to_dict()
            for state in data['states']:
                state['connections'] = []
                for connection in self.node_editor.scene.items():
                    if isinstance(connection, Connection) and connection.start_item.state.get_name() == state['name']:
                        state['connections'].append({
                            'to': connection.end_item.state.get_name(),
                            'pass_context': connection.pass_context
                        })
            with open(file_name, 'w') as f:
                json.dump(data, f)

    def load_state_machine(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load State Machine", "", "JSON Files (*.json)")
        if file_name:
            with open(file_name, 'r') as f:
                data = json.load(f)
                self.node_editor.state_machine = StateMachine.from_dict(data, self.agents)
                self.node_editor.scene.clear()
                node_items = {}
                for state_data in data['states']:
                    state = next(s for s in self.node_editor.state_machine.states if s.get_name() == state_data['name'])
                    node_item = self.node_editor.addNode(state.agent, state_data['x'], state_data['y'])
                    node_items[state.get_name()] = node_item
                for state_data in data['states']:
                    for connection_data in state_data.get('connections', []):
                        from_item = node_items[state_data['name']]
                        to_item = node_items[connection_data['to']]
                        connection = Connection(from_item, to_item, connection_data['pass_context'])
                        self.node_editor.scene.addItem(connection)

    def update_sidebar_on_click(self, state_wrapper):
        state = state_wrapper.get_state()
        self.sidebar.update_properties(state.agent)
        context_text = str(state.context) if state.context else "No context"
        response_text = str(state.get_response()) if state.get_response() else "No response yet"
        self.sidebar.update_context_and_response(context_text, response_text)
        if not self.sidebar.content.isVisible():
            self.toggle_sidebar(True)

    def update_sidebar_with_context_and_response(self, state_wrapper):
        state = state_wrapper.get_state()
        self.sidebar.update_properties(state.agent)
        context_text = str(state.context) if state.context else "No context"
        response_text = str(state.get_response()) if state.get_response() else "No response yet"
        self.sidebar.update_context_and_response(context_text, response_text)
        if not self.sidebar.content.isVisible():
            self.toggle_sidebar(True)

    def run_state_machine(self):
        initial_state = next(iter(self.node_editor.state_machine.states), None)
        if initial_state:
            self.node_editor.state_machine.set_initial_state(initial_state)

            self.thread = QThread()
            self.worker = StateMachineWorker(self.node_editor.state_machine)
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.error.connect(self.handle_error)

            self.thread.start()
        else:
            print("No states in the state machine.")

    def handle_error(self, error_message):
        QMessageBox.critical(self, "Error", f"An error occurred while running the state machine: {error_message}")

    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        super().closeEvent(event)