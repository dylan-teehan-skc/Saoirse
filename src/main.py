import logging; from logging_config import setup_logging
import sys
import sys
from PySide6.QtWidgets import QApplication
from agent_handler.agent import Agent
from agent_handler.task import Task
from gui.gui_main import MainWindow

def create_sample_agents():
    agents = {
        "Researcher": Agent("Researcher", "Gather information", "Specializes in finding and analyzing data", True),
        "Writer": Agent("Writer", "Write the context passed to you", "Skilled in crafting compelling narratives", True),
    }
    return agents

def create_sample_tasks():
    tasks = {
        "Research": Task("Conduct research on Slavoj Zizek", "A comprehensive report on Zizek"),
        "Write": Task("write the context (pprevious conversations) passed to you", "Write a response based on the context passed to you")
    }
    return tasks

def main():
    app = QApplication(sys.argv)

    # Create sample agents and tasks
    agents = create_sample_agents()
    tasks = create_sample_tasks()

    # Assign tasks to agents
    agents["Researcher"].set_task(tasks["Research"])
    agents["Writer"].set_task(tasks["Write"])

    # Create and show the main window
    window = MainWindow()
    window.set_agents(agents)  # Use the new set_agents method
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()