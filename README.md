# Saoirse

## Overview
![image](https://github.com/user-attachments/assets/0a4b7ac5-9e65-4052-b5fe-b4c77a625393)

Saoirse is an agent pipeline and multi agent system editor with a graphical user interface. It allows users to create, visualize, and execute workflows composed of AI agents. The system uses a dynamic LLM (Language Model) wrapper, supporting various AI models, and includes a tool handling system for extended functionality.

## Features

- Graphical node editor for creating agent workflows
- Dynamic LLM wrapper supporting multiple AI models
- Tool handling system for extended agent capabilities
- State machine execution with context passing between agents
- Drag-and-drop interface for adding agents to the workflow
- Save and load functionality for state machines

## Getting Started

### Prerequisites

- Python 3.12
- PySide6
- litellm

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/Atropos-Dad/Saoirse.git
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:
   - Create a `.env` file in the project root
   - Add your API key: `OPENAI_API_KEY=your_api_key_here`

### Running the Application

1. Navigate to the `src` directory:
   ```
   cd src
   ```

2. Run the main script:
   ```
   python main.py
   ```

## How It Works

1. The application starts with a main window (`MainWindow`) that includes a node editor and a sidebar.

2. Users can drag and drop agents from the agent list onto the node editor canvas.

3. Connections between agents can be created by clicking and dragging from one node's output port to another node's input port.

4. The state machine can be executed, which will run each agent's task in the order defined by the connections.

5. The LLM wrapper (`DynamicLLMWrapper`) handles communication with the AI model, supporting various models and tracking usage costs.

6. The tool handling system allows agents to use predefined tools during execution.

7. The state machine execution can pass context between agents, allowing for more complex workflows.

## Code Structure

- `src/main.py`: Entry point of the application
- `src/gui/`: Contains the GUI-related classes (MainWindow, NodeEditor, etc.)
- `src/agent_handler/`: Handles agent-related functionality
- `src/llm_wrap_lib/`: Contains the LLM wrapper for AI model interactions, we use litellm to wrap around openai, anthropic, groq and gemini models
- `src/tool_handler/`: Manages the tool system for extended agent capabilities

## Potential Areas for Expansion

1. Integration with external APIs and services
2. Improved error handling and logging
3. User authentication and higher level project management
4. Collaborative editing features
5. Performance optimizations for large workflows
6. Integration with version control systems
7. Advanced scheduling and conditional execution of agents

## Testing

To run the tests, use the following command from the project root:
```
pytest
```


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the [MIT License](LICENSE).

