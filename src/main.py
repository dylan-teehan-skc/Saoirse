import logging; from logging_config import setup_logging
import sys
import sys
from PySide6.QtWidgets import QApplication
from agent_handler.agent import Agent
from agent_handler.task import Task
from gui.gui_main import MainWindow

def create_sample_agents():
    agents = {
        "Mia": Agent("Mia", "Convince the others you want to go to New York to see Taylor Swift", "A college student who will spend all their money on Taylor Swift", False),
        "Jack": Agent("Jack", "Convice the others to go skiing in France", "Skilled in crafting compelling narratives", False),
        "Dylan": Agent("Dylan", "Convince the others to go to the beach in Dubai", "A beach lover who is persuasive", False),
        "Mediator":Agent("Mediator", "Help the group reach a consensus", "A mediator who can help resolve conflicts", False)
    }
    return agents

def create_sample_tasks():
    tasks = {
        "Negotiate": Task("Negotiate with the group", "Convince the group to choose your destination"),
        "MakeDecision": Task("Make a decision", "Choose a destination for the group")}
    return tasks

def main():
    app = QApplication(sys.argv)

    # Create sample agents and tasks
    agents = create_sample_agents()
    tasks = create_sample_tasks()

    # Create and show the main window
    window = MainWindow()
    window.set_agents(agents)
    window.set_tasks(tasks)  # New: Set the tasks
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()