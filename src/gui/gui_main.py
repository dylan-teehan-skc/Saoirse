import sys
import json
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem, QGraphicsLineItem, QPushButton, QFileDialog, QInputDialog, QComboBox
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPen, QColor, QPainter, QBrush

from gui.state import State, StateMachine
from agent_handler.agent import Agent
from agent_handler.task import Task

class NodeItem(QGraphicsItem):
    def __init__(self, state, x, y):
        super().__init__()
        self.state = state
        self.setPos(x, y)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.connections = []
        self.input_port = Port(self, "input", False)
        self.input_port.setPos(0, 25)
        self.output_port = Port(self, "output", True)
        self.output_port.setPos(90, 25)

    def boundingRect(self):
        return QRectF(0, 0, 100, 50)

    def paint(self, painter, option, widget):
        painter.drawRect(self.boundingRect())
        painter.drawText(10, 20, self.state.get_name())

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.scene():
            for conn in self.connections:
                conn.updatePosition()
        return super().itemChange(change, value)

class Port(QGraphicsEllipseItem):
    def __init__(self, parent, name, is_output):
        super().__init__(0, 0, 10, 10, parent)
        self.name = name
        self.is_output = is_output
        self.setAcceptHoverEvents(True)
        self.setBrush(QBrush(Qt.gray))
        self.setPen(QPen(Qt.black))
        self.setZValue(1)

    def hoverEnterEvent(self, event):
        self.setBrush(QBrush(Qt.red))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setBrush(QBrush(Qt.gray))
        super().hoverLeaveEvent(event)

class Connection(QGraphicsLineItem):
    def __init__(self, start_item, end_item):
        super().__init__()
        self.start_item = start_item
        self.end_item = end_item
        self.setZValue(-1)
        self.setPen(QPen(Qt.green, 2))
        self.start_item.connections.append(self)
        self.end_item.connections.append(self)
        self.updatePosition()

    def updatePosition(self):
        start_pos = self.start_item.mapToScene(self.start_item.output_port.pos() + QPointF(5, 5))
        end_pos = self.end_item.mapToScene(self.end_item.input_port.pos() + QPointF(5, 5))
        self.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())

class NodeEditor(QGraphicsView):
    def __init__(self, agents):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.connection_start = None
        self.current_connection = None
        self.state_machine = StateMachine()
        self.agents = agents
        self.states = {}  # Dictionary to store State objects


    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.scale(zoom_factor, zoom_factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            if isinstance(item, Port) and item.is_output:
                self.connection_start = item.parentItem()
                self.current_connection = QGraphicsLineItem()
                self.current_connection.setPen(QPen(Qt.red, 2))
                self.scene.addItem(self.current_connection)
                self.updateConnection(event.pos())
            else:
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.connection_start:
            self.updateConnection(event.pos())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.connection_start:
            end_item = self.getNodeItemAt(event.pos())
            if isinstance(end_item, NodeItem) and end_item != self.connection_start:
                connection = Connection(self.connection_start, end_item)
                self.scene.addItem(connection)
                self.state_machine.add_transition(self.connection_start.state, end_item.state)
                print(f"Transition created from {self.connection_start.state.get_name()} to {end_item.state.get_name()}")
            self.scene.removeItem(self.current_connection)
            self.current_connection = None
            self.connection_start = None
        super().mouseReleaseEvent(event)

    def updateConnection(self, pos):
        if self.connection_start and self.current_connection:
            start_pos = self.connection_start.mapToScene(self.connection_start.output_port.pos() + QPointF(5, 5))
            end_pos = self.mapToScene(pos)
            self.current_connection.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())

    def getNodeItemAt(self, pos):
        items = self.items(pos)
        for item in items:
            if isinstance(item, NodeItem):
                return item
        return None

    def addNode(self, agent, x, y):
        state = State(agent)
        node_item = NodeItem(state, x, y)
        self.scene.addItem(node_item)
        self.state_machine.add_state(state)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agent-based State Machine Editor")
        self.setGeometry(100, 100, 800, 600)

        self.agents = {}  # This will be set from outside

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

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

        self.node_editor = NodeEditor(self.agents)
        layout.addWidget(self.node_editor)

    def set_agents(self, agents):
        self.agents = agents
        self.agent_combo.clear()
        self.agent_combo.addItems(self.agents.keys())
        self.node_editor.agents = self.agents

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
            with open(file_name, 'w') as f:
                json.dump(self.node_editor.state_machine.to_dict(), f)

    def load_state_machine(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load State Machine", "", "JSON Files (*.json)")
        if file_name:
            with open(file_name, 'r') as f:
                data = json.load(f)
                self.node_editor.state_machine = StateMachine.from_dict(data, self.agents)
                self.node_editor.scene.clear()
                for state in self.node_editor.state_machine.states:
                    self.node_editor.addNode(state.agent, 0, 0)
                for from_state, transitions in self.node_editor.state_machine.states.items():
                    for transition in transitions:
                        from_item = next(item for item in self.node_editor.scene.items() if isinstance(item, NodeItem) and item.state == from_state)
                        to_item = next(item for item in self.node_editor.scene.items() if isinstance(item, NodeItem) and item.state == transition.target_state)
                        connection = Connection(from_item, to_item)
                        self.node_editor.scene.addItem(connection)

    def run_state_machine(self):
        initial_state = next(iter(self.node_editor.state_machine.states), None)
        if initial_state:
            self.node_editor.state_machine.set_initial_state(initial_state)
            try:
                self.node_editor.state_machine.run()
            except Exception as e:
                print(f"An error occurred while running the state machine: {str(e)}")
        else:
            print("No states in the state machine.")