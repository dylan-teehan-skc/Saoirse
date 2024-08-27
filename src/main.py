import logging
from logging_config import setup_logging
import sys
from PySide6.QtWidgets import QApplication
from agent_handler.agent import Agent
from agent_handler.task import Task
from gui.gui_main import MainWindow

def create_sample_agents():
    agents = {
        "Researcher": Agent("Researcher", "Gather information", "Specializes in finding and analyzing data", True),
        "Writer": Agent("Writer", "Create content", "Skilled in crafting compelling narratives", True),
        "Editor": Agent("Editor", "Refine content", "Expert in improving and polishing written work", True),
        
    }
    return agents

def create_sample_tasks():
    tasks = {
        "Research": Task("Conduct research on AI advancements", "A comprehensive report on recent AI breakthroughs"),
        "Write": Task("Write an article on AI ethics", "A 1000-word article discussing ethical considerations in AI"),
        "Edit": Task("Edit the AI ethics article", "A polished version of the AI ethics article"),
        
    }
    return tasks

def main():
    app = QApplication(sys.argv)

    # Create sample agents and tasks
    agents = create_sample_agents()
    tasks = create_sample_tasks()

    # Assign tasks to agents
    for agent, task in zip(agents.values(), tasks.values()):
        agent.set_task(task)

    # Create and show the main window
    window = MainWindow()
    window.set_agents(agents)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()