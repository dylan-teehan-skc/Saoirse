from crewai import Agent, Task, Crew, Pipeline
from crewai.routers.router import Router, Route
from crewai.process import Process
import sqlite3
from langchain.tools import Tool
from langchain.agents import tool
import random
from datetime import datetime, timedelta
import asyncio
from langchain_openai import ChatOpenAI

class SQLiteDatabase:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            return f"SQLite error: {e}"

    def execute_many(self, query, data):
        try:
            self.cursor.executemany(query, data)
            self.conn.commit()
        except sqlite3.Error as e:
            return f"SQLite error: {e}"

    def get_schema(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        schema = {}
        for table in tables:
            table_name = table[0]
            self.cursor.execute(f"PRAGMA table_info({table_name});")
            columns = self.cursor.fetchall()
            schema[table_name] = [column[1] for column in columns]
        return schema

def generate_demo_data(db_path):
    db = SQLiteDatabase(db_path)

    # Create tables
    db.execute_query('''
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT
    )
    ''')

    db.execute_query('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date TEXT,
        total_amount REAL,
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    )
    ''')

    # Generate customer data
    customers = [
        (i, f"Customer {i}", f"customer{i}@example.com")
        for i in range(1, 101)
    ]
    db.execute_many("INSERT INTO customers (customer_id, name, email) VALUES (?, ?, ?)", customers)

    # Generate order data
    orders = []
    start_date = datetime(2023, 1, 1)
    for _ in range(1000):
        customer_id = random.randint(1, 100)
        order_date = start_date + timedelta(days=random.randint(0, 365))
        total_amount = round(random.uniform(10, 1000), 2)
        orders.append((customer_id, order_date.strftime('%Y-%m-%d'), total_amount))

    db.execute_many("INSERT INTO orders (customer_id, order_date, total_amount) VALUES (?, ?, ?)", orders)

    print("Demo data generated successfully.")

# Initialize the database
db_path = "demo_database.db"
db = SQLiteDatabase(db_path)
generate_demo_data(db_path)

# Tools
@tool
def examine_schema(query: str) -> str:
    """Examine the database schema and infer semantics."""
    schema = db.get_schema()
    return f"Database schema: {schema}"

@tool
def execute_sql(query: str) -> str:
    """Execute a SQL query and return the results."""
    return str(db.execute_query(query))

@tool
def test_query_speed(query: str) -> str:
    """Test the speed of a SQL query."""
    import time
    start_time = time.time()
    result = db.execute_query(query)
    end_time = time.time()
    if isinstance(result, str) and result.startswith("SQLite error"):
        return f"Error: {result}"
    return f"Query execution time: {end_time - start_time} seconds"

# Agents
schema_analyst = Agent(
    name="Schema Analyst",
    role='Database Schema Expert',
    goal='Examine the database schema and infer semantics',
    backstory='You are an expert in database design and can quickly understand table relationships.',
    tools=[examine_schema],
    verbose=True
)

sql_translator = Agent(
    name="SQL Translator",
    role='Natural Language to SQL Converter',
    goal='Translate user requests into SQL queries',
    backstory='You are skilled in converting natural language to complex SQL queries, including joins.',
    tools=[execute_sql],
    verbose=True
)

sql_tester = Agent(
    name="SQL Bug fixer",
    role='SQL Query Validator and testing',
    goal='Test SQL queries for errors and suggest fixes',
    backstory='You are meticulous in finding and reporting SQL errors. You also provide suggestions for fixing errors.',
    tools=[execute_sql],
    verbose=True
)

data_validator = Agent(
    name="Data Validator",
    role='Query Result Analyst',
    goal='Validate query results against expected data',
    backstory='You have a keen eye for data inconsistencies and can quickly spot anomalies.',
    tools=[execute_sql],
    verbose=True
)

performance_analyst = Agent(
    name="Performance Analyst",
    role='Query Performance Expert',
    goal='Analyze query performance',
    backstory='You are an expert in optimizing database queries for speed.',
    tools=[test_query_speed],
    verbose=True
)

# Manager Agent
# manager_agent = Agent(
#     name="Manager Agent",
#     role="Task Manager",
#     goal="Manage and delegate tasks to other agents for efficient execution",
#     backstory="You are responsible for ensuring that all tasks are properly assigned and completed.",
#     tools=[],
#     allow_delegation=True,
#     verbose=True
# )

## Tasks
def create_tasks(user_request):
    final_output = None  # To store the final result and stop further processing
    
    def stop_if_final_output(output):
        nonlocal final_output
        if "final answer" in output.lower():  # Condition to check for final answer
            final_output = output
            return False  # Stop further execution
        return True
    tasks = [
        Task(
            description=f'Translate the user request into a SQL query. User request: "{user_request}"',
            expected_output="A SQL query that addresses the user's request."
        ),
        Task(
            description='Test the generated SQL query for errors. If errors are found, suggest fixes.',
            expected_output="A report on the SQL query's correctness and any suggested fixes if errors are found.",
            condition=lambda output: stop_if_final_output(output)
        ),
        Task(
            description='Validate the query results against expected data based on the user request.',
            expected_output="A validation report of the query results compared to expected data.",
            condition=lambda output: stop_if_final_output(output)
        ),
        Task(
            description='Analyze the performance of the SQL query',
            expected_output="A performance analysis report of the SQL query execution.",
            condition=lambda output: stop_if_final_output(output)
        )
    ]
    return tasks, final_output

# Main pipeline
def create_main_pipeline(user_request):
    tasks, final_output = create_tasks(user_request)
    return Pipeline(stages=[
        Crew(
            agents=[schema_analyst, sql_translator, sql_tester, data_validator, performance_analyst],
            tasks=tasks,
            process=Process.hierarchical,
            memory=True,
            manager_llm=ChatOpenAI(temperature=0, model="gpt-4"),
            verbose=True,
            planning=True,
            max_iter=2
        )
    ]), final_output

# Main execution
async def process_user_request(user_request):
    try:
        pipeline, final_output = create_main_pipeline(user_request)
        result = await pipeline.process_single_kickoff(kickoff_input={"user_request": user_request})
        if final_output:
            print("Final Output:", final_output)
        else:
            print("Process completed without early exit.")
        return result
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

# Example usage
user_request = "Show me the top 5 customers by total order amount"
async def main():
    result = await process_user_request(user_request)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())