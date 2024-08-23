import logging; from logging_config import setup_logging
from agent.agent_creation import complete_tasks
# Set up logging
# logger = setup_logging()


def main():
    complete_tasks()
    print("tasks completed")
    # logger.debug("Main function executed")

if __name__ == "__main__":
    main()
    
    
    
    

