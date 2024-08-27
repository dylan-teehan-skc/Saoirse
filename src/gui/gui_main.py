import sys
import json
from PySide6.QtWidgets import (
    QFrame, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QGraphicsView, QGraphicsScene, 
    QGraphicsItem, QGraphicsEllipseItem, QGraphicsLineItem, QPushButton, QFileDialog, QInputDialog, QComboBox, QSplitter, 
    QLabel, QCheckBox, QGraphicsProxyWidget, QApplication, QMessageBox, QScrollArea
)
from PySide6.QtCore import (
    Qt, QPointF, QRectF, Signal, QObject, QSize, QMimeData, QThread, Slot 
)
from PySide6.QtGui import (
    QPen, QColor, QPainter, QBrush, QDrag, QPixmap
)
from gui.state import State, StateMachine, StateWrapper
from agent_handler.agent import Agent
from agent_handler.task import Task

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

class DraggableAgentWidget(QLabel):
    def __init__(self, agent, parent=None):
        super().__init__(parent)
        self.agent = agent
        self.setText(self.format_text(agent.get_name()))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 1px solid black; padding: 5px;")
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

        self.context_label = QLabel()
        self.context_label.setWordWrap(True)
        self.response_label = QLabel()
        self.response_label.setWordWrap(True)

        content_layout.addWidget(QLabel("Context:"))
        content_layout.addWidget(self.context_label)
        content_layout.addWidget(QLabel("Response:"))
        content_layout.addWidget(self.response_label)
        content_layout.addStretch()

        # Add toggle bar and content to main layout
        self.layout.addWidget(self.toggle_bar)
        self.layout.addWidget(self.content)
        
        self.content.hide()


    def update_context_and_response(self, context, response):
        self.context_label.setText(context)
        self.response_label.setText(response)

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
        self.is_highlighted = False

    def boundingRect(self):
        return QRectF(0, 0, 100, 50)

    def paint(self, painter, option, widget):
        if self.is_highlighted:
            painter.setBrush(QBrush(Qt.yellow))
        else:
            painter.setBrush(QBrush(Qt.white))
        painter.drawRect(self.boundingRect())
        painter.drawText(10, 20, self.state.get_name())

    def highlight(self, highlight=True):
        self.is_highlighted = highlight
        self.update()


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
    def __init__(self, start_item, end_item, pass_context=False):
        super().__init__()
        self.start_item = start_item
        self.end_item = end_item
        self.pass_context = pass_context
        self.setZValue(-1)
        self.setPen(QPen(Qt.green, 2))
        self.start_item.connections.append(self)
        self.end_item.connections.append(self)
        self.updatePosition()

        # Add a checkbox for context passing
        self.context_checkbox = QCheckBox("Pass Context")
        self.context_checkbox.setChecked(pass_context)
        self.context_checkbox.stateChanged.connect(self.toggleContextPassing)

        # Add the checkbox to the scene
        self.checkbox_proxy = QGraphicsProxyWidget(self)
        self.checkbox_proxy.setWidget(self.context_checkbox)
        self.updateCheckboxPosition()

    def toggleContextPassing(self, state):
        self.pass_context = (state == Qt.Checked)

    def updatePosition(self):
        start_pos = self.start_item.mapToScene(self.start_item.output_port.pos() + QPointF(5, 5))
        end_pos = self.end_item.mapToScene(self.end_item.input_port.pos() + QPointF(5, 5))
        self.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())
        self.updateCheckboxPosition()

    def updateCheckboxPosition(self):
        if self.scene():
            line = self.line()
            center = line.pointAt(0.5)
            self.checkbox_proxy.setPos(center)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        if self.pass_context:
            painter.drawText(self.boundingRect().center(), "Context")

class NodeEditor(QGraphicsView):
    node_clicked = Signal(StateWrapper)  # Changed to emit StateWrapper
    node_properties_updated = Signal(StateWrapper)

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

        self.state_machine = StateMachine()
        self.state_machine.state_changed.connect(self.on_state_changed)
        self.state_machine.execution_finished.connect(self.clear_highlights)

        self.connection_start = None
        self.current_connection = None
        self.agents = agents
        self.states = {}  # Dictionary to store State objects
        self.setAcceptDrops(True)


    @Slot(StateWrapper)
    def on_state_changed(self, state_wrapper):
        for item in self.scene.items():
            if isinstance(item, NodeItem):
                item.highlight(item.state == state_wrapper.get_state())
        self.node_properties_updated.emit(state_wrapper)
        # Connect to the response_ready signal
        state_wrapper.response_ready.connect(self.on_response_ready)

    @Slot(str)
    def on_response_ready(self, response):
        # Update the UI with the new response
        current_state = self.state_machine.current_state
        if current_state:
            state_wrapper = StateWrapper(current_state)
            state_wrapper.update_response(response)
            self.node_properties_updated.emit(state_wrapper)

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
                event.setDropAction(Qt.MoveAction)
                event.accept()
                print(f"Dropped: {agent_name} at ({pos.x()}, {pos.y()})")

    def on_node_clicked(self, state):
        print(f"NodeEditor received click for state: {state.get_name()}")
        self.node_clicked.emit(StateWrapper(state))  # Emit StateWrapper

    def addNode(self, agent, x, y):
        state = State(agent)
        node_item = NodeItem(state, x, y)
        node_item.signals.clicked.connect(self.on_node_clicked)
        self.scene.addItem(node_item)
        self.state_machine.add_state(state)
       
        print(f"Added node for agent: {agent.get_name()}")  # Debug print
        return node_item  # Return the created node_item

    
    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.scale(zoom_factor, zoom_factor)

    def mouseMoveEvent(self, event):
        if self.connection_start:
            self.updateConnection(event.pos())
        super().mouseMoveEvent(event)

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
    

    @Slot(StateWrapper)
    def highlight_current_node(self, state_wrapper):
        state = state_wrapper.get_state()
        for item in self.scene.items():
            if isinstance(item, NodeItem):
                item.highlight(item.state == state)
        self.node_properties_updated.emit(state_wrapper)


    @Slot()
    def clear_highlights(self):
        for item in self.scene.items():
            if isinstance(item, NodeItem):
                item.highlight(False)

#for the grid background
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agent-based State Machine Editor")
        self.setGeometry(100, 100, 1000, 600)

        self.agents = {}  # This will be set from outside

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

        # Add draggable agents list
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
            data = self.node_editor.state_machine.to_dict()
            # Add context passing information to the data
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

            # Create a new thread and worker
            self.thread = QThread()
            self.worker = StateMachineWorker(self.node_editor.state_machine)
            self.worker.moveToThread(self.thread)

            # Connect signals and slots
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.error.connect(self.handle_error)

            # Start the thread
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




