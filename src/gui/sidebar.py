from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal, QSize

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