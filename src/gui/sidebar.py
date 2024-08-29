from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QLabel, QScrollArea
from PySide6.QtCore import Qt, Signal, QSize

class ExpandableLabel(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.title = title
        self.title_label = QLabel(f"{title}:")
        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.expand_button = QPushButton("Expand")
        self.expand_button.clicked.connect(self.toggle_expand)
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.content_label)
        self.layout.addWidget(self.expand_button)
        self.expanded = False
        self.full_text = ""

    def set_text(self, text):
        self.full_text = text
        self.update_text()

    def update_text(self):
        if self.expanded:
            self.content_label.setText(self.full_text)
            self.expand_button.setText("Collapse")
        else:
            self.content_label.setText(self.full_text[:100] + "..." if len(self.full_text) > 100 else self.full_text)
            self.expand_button.setText("Expand")

    def toggle_expand(self):
        self.expanded = not self.expanded
        self.update_text()

class Sidebar(QWidget):
    toggle_signal = Signal(bool)

    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.toggle_bar = QFrame()
        self.toggle_bar.setFixedWidth(30)
        toggle_bar_layout = QVBoxLayout(self.toggle_bar)
        toggle_bar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.toggle_button = QPushButton("►")
        self.toggle_button.setFixedSize(QSize(25, 50))
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        toggle_bar_layout.addWidget(self.toggle_button)
        toggle_bar_layout.addStretch()

        self.content = QScrollArea()
        self.content.setWidgetResizable(True)
        self.content.setFixedWidth(250)
        
        content_widget = QWidget()
        self.content.setWidget(content_widget)
        content_layout = QVBoxLayout(content_widget)
        
        self.name_label = QLabel()
        self.name_label.setWordWrap(True)
        self.goal_label = QLabel()
        self.goal_label.setWordWrap(True)
        self.backstory_label = QLabel()
        self.backstory_label.setWordWrap(True)
        
        content_layout.addWidget(self.name_label)
        content_layout.addWidget(self.goal_label)
        content_layout.addWidget(self.backstory_label)
        content_layout.addSpacing(10)

        self.task_label = QLabel()
        self.task_label.setWordWrap(True)
        content_layout.addWidget(QLabel("Task:"))
        content_layout.addWidget(self.task_label)

        self.context_label = ExpandableLabel("Context")
        self.response_label = ExpandableLabel("Response")

        content_layout.addWidget(self.context_label)
        content_layout.addWidget(self.response_label)
        content_layout.addStretch()

        self.layout.addWidget(self.toggle_bar)
        self.layout.addWidget(self.content)
        
        self.content.hide()

    def update_properties(self, agent):
        self.name_label.setText(f"Name: {agent.get_name()}")
        self.goal_label.setText(f"Goal: {agent.get_goal()}")
        self.backstory_label.setText(f"Backstory: {agent.get_backstory()}")

    def update_context_and_response(self, context, response, task):
        self.task_label.setText(task)
        self.context_label.set_text(context)
        self.response_label.set_text(response)

    def toggle_sidebar(self):
        is_expanded = self.content.isVisible()
        self.content.setVisible(not is_expanded)
        self.toggle_signal.emit(not is_expanded)
        self.toggle_button.setText("◄" if not is_expanded else "►")

    def showEvent(self, event):
        super().showEvent(event)
        self.content.hide()