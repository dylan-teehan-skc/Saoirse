from agent_handler.agent import Agent
from agent_handler.task import Task

def complete_tasks():
    Mia = Agent(
        name="Mia",
        goal="to go to dubai",
        backstory="I am a student so prices should be cheap",
        verbose=True)

    Dylan = Agent(
        name="Dylan",
        goal="to go to Dublin",
        backstory="I have alot of money!",
        verbose=True)

    Mediator = Agent(
        name="Mediator",
        goal="to help both parties reach an agreement",
        backstory="I am a mediator",
        verbose=True)
    

    # if you have generic tasks that ur repeating. Instead 
    # having the tasks have assigned agents. Better to give 
    # the agents the asigned tasks
    # i.e Dylan_agent.set_task(travel_task: Task)
    mia_task = Task(
        description="Explain where you want to go and why",
        expected_output="An explanation of where you want to go with your reasoning and pricepoints",
        output_json=False)
    
        
    dylan_task = Task(
        description="Explain where you want to go and why",
        expected_output="An explanation of where you want to go with your reasoning and pricepoints",
        output_json=False)

    Dylan.set_task(dylan_task)
    Mia.set_task(mia_task)

    Dylan.complete_task()
    Mia.complete_task()


