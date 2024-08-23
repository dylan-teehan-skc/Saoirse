from crewai import Agent, Task, Crew, Process

# Define the agents

story_editor = Agent(
    name="Story Editor",
    role="Creates the overall episode outline and plot structure",
    goal="Ensure the episode's story arc is coherent and engaging",
    backstory="Veteran writer with a deep understanding of Friends' narrative style"
)

ross_writer = Agent(
    name="Ross Writer",
    role="Writes Ross's dialogue and scenes",
    goal="Capture Ross's neurotic yet endearing personality",
    backstory="Specializes in writing awkward and intellectual humor"
)

rachel_writer = Agent(
    name="Rachel Writer",
    role="Writes Rachel's dialogue and scenes",
    goal="Showcase Rachel's charm and occasional ditziness",
    backstory="Expert in writing fashion-forward, humorous dialogue"
)

chandler_writer = Agent(
    name="Chandler Writer",
    role="Writes Chandler's dialogue and scenes",
    goal="Provide Chandler's sarcastic and self-deprecating humor",
    backstory="Known for sharp wit and impeccable timing in dialogue"
)

monica_writer = Agent(
    name="Monica Writer",
    role="Writes Monica's dialogue and scenes",
    goal="Highlight Monica's competitive nature and maternal instincts",
    backstory="Excels at writing fastidious, high-energy characters"
)

phoebe_writer = Agent(
    name="Phoebe Writer",
    role="Writes Phoebe's dialogue and scenes",
    goal="Infuse scenes with Phoebe's quirky and eccentric humor",
    backstory="Master of crafting surreal and whimsical humor"
)

joey_writer = Agent(
    name="Joey Writer",
    role="Writes Joey's dialogue and scenes",
    goal="Deliver Joey's lovable and sometimes clueless humor",
    backstory="Specializes in writing affable and simple-minded characters"
)

junior_writer = Agent(
    name="Junior Writer",
    role="Refines the script and adds extra humor",
    goal="Enhance jokes and ensure comedic timing is perfect",
    backstory="Eager and fresh writer with a knack for punchlines"
)

script_formatter = Agent(
    name="Script Formatter",
    role="Ensures the script follows proper TV script format",
    goal="Format the final script according to industry standards",
    backstory="Experienced in TV script formatting and industry conventions"
)

scene_writer = Agent(
    name="Scene Writer",
    role="Develops individual scenes based on the story outline",
    goal="Create engaging and funny scenes that fit the Friends style",
    backstory="Expert in sitcom pacing and scene structure"
)

# Modify the create_tasks function
def create_tasks(prompt):
    # List of characters and corresponding agents
    characters = [
        ("Ross", ross_writer),
        ("Rachel", rachel_writer),
        ("Chandler", chandler_writer),
        ("Monica", monica_writer),
        ("Phoebe", phoebe_writer),
        ("Joey", joey_writer)
    ]
    
    # Start with the initial tasks
    tasks = [
        Task(
            description=f"Develop a detailed episode outline based on the prompt: {prompt}. Include main plot and subplots.",
            agent=story_editor
        ),
        Task(
            description="Write a teaser scene that sets up the episode's premise",
            agent=scene_writer
        ),
        Task(
            description="Develop 3-4 main scenes that progress the story, assigning them to appropriate settings (apartment, coffee house, etc.)",
            agent=scene_writer
        )
    ]
    
    # Add tasks for each character using a loop
    for character, writer in characters:
        tasks.append(
            Task(
                description=f"Write {character}'s dialogue and actions throughout the episode",
                agent=writer
            )
        )
    
    # Add the remaining tasks
    tasks.extend([
        Task(
            description="Refine the script, improve joke timing, and add additional comedic elements",
            agent=junior_writer
        ),
        Task(
            description="Format the entire script according to TV script standards, including scene headings, action lines, and dialogue formatting",
            agent=script_formatter
        )
    ])
    
    return tasks

# Create the Crew
friends_crew = Crew(
    agents=[story_editor, scene_writer, ross_writer, rachel_writer, chandler_writer, 
            monica_writer, phoebe_writer, joey_writer, junior_writer, script_formatter],
    tasks=create_tasks("The gang goes on a camping trip, but everything that can go wrong does"),
    process=Process.sequential
)

# Run the crew to generate the script
result = friends_crew.kickoff()

# Save the result to a file
with open("friends_episode_script.txt", "w") as file:
    file.write(result)

print("Script has been generated and saved to 'friends_episode_script.txt'")
