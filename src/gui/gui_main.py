import sys
import json
from PySide6.QtWidgets import QFrame, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem, QGraphicsLineItem, QPushButton, QFileDialog, QInputDialog, QComboBox, QSplitter, QLabel
from PySide6.QtCore import Qt, QPointF, QRectF, Signal, QObject, QSize
from PySide6.QtGui import QPen, QColor, QPainter, QBrush

from gui.state import State, StateMachine
from agent_handler.agent import Agent
from agent_handler.task import Task
#from .sidebar import Sidebar

from PySide6.QtWidgets import QComboBox, QApplication, QScrollArea
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag, QPixmap

#drag component doesnt work yet kill me but that's tommorow me problemos
from PySide6.QtWidgets import QComboBox, QApplication
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag, QPixmap, QPainter

class DraggableAgentWidget(QLabel):
    def __init__(self, agent, parent=None):
        super().__init__(parent)
        self.agent = agent
        self.setText(self.format_text(agent.get_name()))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 1px solid black; padding: 5px;")
        # self.setStyleSheet("""
        #     QLabel {
        #         border: 1px solid black;
        #         background-color: white;
        #         padding: 5px;
        #         font-weight: bold;
        #     }
        # """)
        self.setFixedSize(100, 50)
    
    def format_text(self, text):
        words = text.split()
        if len(words) > 1:
            mid = len(words) // 2
            return '\n'.join([' '.join(words[:mid]), ' '.join(words[mid:])])
        return text


    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(self.agent.get_name())
        drag.setMimeData(mime_data)

        pixmap = QPixmap(self.size())
        self.render(pixmap)
        drag.setPixmap(pixmap)

        drag.exec(Qt.DropAction.CopyAction)
    
class Sidebar(QWidget):
    toggle_signal = Signal(bool)

    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # Create a narrow bar for the toggle button
        self.toggle_bar = QFrame()
        self.toggle_bar.setFixedWidth(30)
        toggle_bar_layout = QVBoxLayout(self.toggle_bar)
        toggle_bar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.toggle_button = QPushButton("►")  # Right arrow for expand
        self.toggle_button.setFixedSize(QSize(25, 50))
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        toggle_bar_layout.addWidget(self.toggle_button)
        toggle_bar_layout.addStretch()

        # Create the main content area
        self.content = QWidget()
        self.content.setFixedWidth(170)  
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(5, 5, 5, 5)  
        
        self.name_label = QLabel()
        self.name_label.setWordWrap(True)
        self.goal_label = QLabel()
        self.goal_label.setWordWrap(True)
        self.backstory_label = QLabel()
        self.backstory_label.setWordWrap(True)
        
        content_layout.addWidget(self.name_label)
        content_layout.addWidget(self.goal_label)
        content_layout.addWidget(self.backstory_label)
        content_layout.addStretch()

        # Add toggle bar and content to main layout
        self.layout.addWidget(self.toggle_bar)
        self.layout.addWidget(self.content)
        
        self.content.hide()

    def update_properties(self, agent):
        self.name_label.setText(f"Name: {agent.get_name()}")
        self.goal_label.setText(f"Goal: {agent.get_goal()}")
        self.backstory_label.setText(f"Backstory: {agent.get_backstory()}")

    def toggle_sidebar(self):
        is_expanded = self.content.isVisible()
        self.content.setVisible(not is_expanded)
        self.toggle_signal.emit(not is_expanded)
        self.toggle_button.setText("◄" if not is_expanded else "►")

    def showEvent(self, event):
        super().showEvent(event)
        self.content.hide() 

class NodeSignals(QObject):
    clicked = Signal(object)

class NodeItem(QGraphicsItem):
    # clicked = Signal(Agent)

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
        self.connections = []
        self.signals = NodeSignals()

    def boundingRect(self):
        return QRectF(0, 0, 100, 50)

    def paint(self, painter, option, widget):

        painter.setBrush(QBrush(Qt.white))
        painter.drawRect(self.boundingRect())
        painter.drawText(10, 20, self.state.get_name())


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.signals.clicked.emit(self.state)
        super().mousePressEvent(event)

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
    node_clicked = Signal(object)  # Signal to emit when a node is clicked

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
        self.states = {} 
        self.setAcceptDrops(True)
        
        self.setDragMode(QGraphicsView.NoDrag)

    def drawBackground(self, painter, rect):
 
        super().drawBackground(painter, rect)

        # we could do bigger/smaller if u want
        grid_size = 20

        pen = QPen(QColor(200, 200, 200), 0.5)
        painter.setPen(pen)
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)

        # Draw vertical lines
        for x in range(left, int(rect.right()), grid_size):
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))

        # Draw horizontal lines
        for y in range(top, int(rect.bottom()), grid_size):
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)

   

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            agent_name = event.mimeData().text()
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                pos = self.mapToScene(event.pos())
                self.addNode(agent, pos.x(), pos.y())
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def addNode(self, agent, x, y):
        state = State(agent)
        node_item = NodeItem(state, x, y)
        node_item.signals.clicked.connect(self.node_clicked)
        self.scene.addItem(node_item)
        self.state_machine.add_state(state)
       
        print(f"Added node for agent: {agent.get_name()}")  # Debug print

    
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


#for the grid background
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

        #NORMAL DROPDOWN AGENTS SYSTEM
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

        #THIS IS DRAG AND DROP AGENTS SYSTEM
        self.agents_list = QListWidget()
        self.agents_list.setFlow(QListWidget.LeftToRight)
        self.agents_list.setWrapping(False)
        self.agents_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.agents_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.agents_list.setMaximumHeight(52)  # Adjust as needed
        content_layout.addWidget(QLabel("Draggable Agents:"))
        content_layout.addWidget(self.agents_list)
        

        self.node_editor = NodeEditor(self.agents)
        content_layout.addWidget(self.node_editor)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(content_widget)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)


        self.node_editor.node_clicked.connect(self.update_sidebar)
    def toggle_sidebar(self, show):
        if show:
            self.sidebar.content.show()
        else:
            self.sidebar.content.hide()

    def update_sidebar(self, agent):
        self.sidebar.update_properties(agent)
        if not self.sidebar.content.isVisible():
            self.toggle_sidebar(True)
    # def update_sidebar(self, agent):
    #     print(f"MainWindow updating sidebar for agent: {agent.get_name()}")  # Debug print
    #     self.sidebar.update_properties(agent)

    

    def set_agents(self, agents):
        self.agents = agents
        self.agent_combo.clear()
        self.agent_combo.addItems(self.agents.keys())
        self.node_editor.agents = self.agents
        
        # Add draggable agent widgets
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
                print(f"An error occurred while running the state machine: {str(e)} ")
        else:
            print("No states in the state machine.")




