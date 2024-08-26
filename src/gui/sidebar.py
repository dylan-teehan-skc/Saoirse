# from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea
# from PySide6.QtCore import Qt
# from agent_handler.agent import Agent

# class Sidebar(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.layout = QVBoxLayout(self)
#         self.scroll_area = QScrollArea()
#         self.scroll_widget = QWidget()
#         self.scroll_layout = QVBoxLayout(self.scroll_widget)

#         self.agent_name = QLabel()
#         self.agent_goal = QLabel()
#         self.agent_backstory = QLabel()
#         self.agent_verbose = QLabel()

#         self.scroll_layout.addWidget(self.agent_name)
#         self.scroll_layout.addWidget(self.agent_goal)
#         self.scroll_layout.addWidget(self.agent_backstory)
#         self.scroll_layout.addWidget(self.agent_verbose)
#         self.scroll_layout.addStretch()

#         self.scroll_area.setWidgetResizable(True)
#         self.scroll_area.setWidget(self.scroll_widget)

#         self.layout.addWidget(self.scroll_area)

#         self.toggle_button = QPushButton("Hide Sidebar")
#         self.toggle_button.clicked.connect(self.toggle_visibility)
#         self.layout.addWidget(self.toggle_button)

#     def update_properties(self, agent):
#         self.agent_name.setText(f"Name: {agent.get_name()}")
#         self.agent_goal.setText(f"Goal: {agent.get_goal()}")
#         self.agent_backstory.setText(f"Backstory: {agent.get_backstory()}")
#         self.agent_verbose.setText(f"Verbose: {agent.get_verbose()}")

#     def toggle_visibility(self):
#         if self.isVisible():
#             self.hide()
#             self.toggle_button.setText("Show Sidebar")
#         else:
#             self.show()
#             self.toggle_button.setText("Hide Sidebar")