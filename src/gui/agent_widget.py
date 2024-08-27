from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag, QPixmap

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