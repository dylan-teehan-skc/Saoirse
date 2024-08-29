from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsLineItem, QGraphicsItem, QGraphicsEllipseItem
from PySide6.QtCore import Qt, Signal, Slot, QPointF, QRectF, QObject
from PySide6.QtGui import QPen, QColor, QPainter, QBrush

from gui.state import State, StateWrapper, StateMachine

class NodeSignals(QObject):
    clicked = Signal(object)

class NodeItem(QGraphicsItem):
    def __init__(self, state, x, y, parent_editor):
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
        self.parent_editor = parent_editor

    def boundingRect(self):
        return QRectF(0, 0, 100, 50)

    def paint(self, painter, option, widget):
        if self.is_highlighted:
            painter.setBrush(QBrush(Qt.yellow))
        else:
            painter.setBrush(QBrush(QColor(0, 206, 209)))
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
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.parent_editor.update_last_node_pos(self.pos())
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
    node_clicked = Signal(StateWrapper)
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
        self.nodes = {}
        self.setAcceptDrops(True)

        self.last_node_pos = QPointF(0, 0)
        self.node_spacing = 120

        self.context_passing = {}

    def update_last_node_pos(self, pos):
        self.last_node_pos = pos

    @Slot(StateWrapper)
    def on_state_changed(self, state_wrapper):
        for item in self.scene.items():
            if isinstance(item, NodeItem):
                item.highlight(item.state == state_wrapper.get_state())
        self.node_properties_updated.emit(state_wrapper)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        grid_size = 20
        pen = QPen(QColor(200, 200, 200), 0.5)
        painter.setPen(pen)
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)
        for x in range(left, int(rect.right()), grid_size):
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
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
                event.setDropAction(Qt.DropAction.MoveAction)
                event.accept()

    def on_node_clicked(self, state):
        self.node_clicked.emit(StateWrapper(state))

    def addNode(self, agent, x=None, y=None):
        if x is None or y is None:
            x = self.last_node_pos.x() + self.node_spacing
            y = self.last_node_pos.y()

        state = State(agent)
        node_item = NodeItem(state, x, y, self)
        node_item.signals.clicked.connect(self.on_node_clicked)
        self.scene.addItem(node_item)
        self.state_machine.add_state(state)
        self.nodes[state.get_name()] = node_item
        
        self.last_node_pos = QPointF(x, y)
        
        return node_item

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        zoom_factor = zoom_in_factor if event.angleDelta().y() > 0 else zoom_out_factor
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

    @Slot()
    def clear_highlights(self):
        for item in self.scene.items():
            if isinstance(item, NodeItem):
                item.highlight(False)

    def get_clicked_state(self):
        for item in self.scene.selectedItems():
            if isinstance(item, NodeItem):
                return item.state
        return None

    def should_pass_context(self, from_state, to_agent_name):
        return self.context_passing.get(from_state.get_name(), {}).get(to_agent_name, False)

    def set_context_passing(self, from_state, to_agent_name, should_pass):
        if from_state.get_name() not in self.context_passing:
            self.context_passing[from_state.get_name()] = {}
        self.context_passing[from_state.get_name()][to_agent_name] = should_pass
        self.state_machine.set_context_passing(from_state.get_name(), to_agent_name, should_pass)

    def load_state_machine(self, data, agents):
        self.state_machine = StateMachine.from_dict(data, agents)
        self.scene.clear()
        self.nodes.clear()
        for state_data in data['states']:
            state = next(s for s in self.state_machine.states if s.get_name() == state_data['name'])
            node_item = self.addNode(state.agent, state_data['x'], state_data['y'])
            self.nodes[state.get_name()] = node_item
        for state_data in data['states']:
            for connection_data in state_data.get('connections', []):
                from_item = self.nodes[state_data['name']]
                to_item = self.nodes[connection_data['to']]
                connection = Connection(from_item, to_item)
                self.scene.addItem(connection)
        
        self.context_passing = data.get('context_passing', {})
        self.state_machine.context_passing = self.context_passing