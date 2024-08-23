from agent.agent import Agent
from agent.task import Task

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
    
    Mia.complete_task(
        description="Explain where you want to go and why",
        expected_output="An explanation of where you want to go with your reasoning and pricepoints",
        output_json=False)
        
    Dylan.complete_task(
        description="Explain where you want to go and why",
        expected_output="An explanation of where you want to go with your reasoning and pricepoints",
        output_json=False)



