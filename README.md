# AI Tutor Agent for A2A Protocol

An intelligent tutor agent powered by CrewAI that helps students understand their learning gaps and designs personalized learning materials based on topics of their choice. This agent is integrated with the A2A protocol for interoperability with other agents.

## Features

- **Learning Gap Assessment**: Analyzes a student's current knowledge level and identifies specific gaps
- **Personalized Learning Plans**: Creates customized learning plans tailored to individual needs
- **Resource Recommendations**: Suggests relevant learning resources based on the identified gaps
- **Learning Milestones**: Provides clear milestones to track progress
- **A2A Protocol Integration**: Exposes the tutor agent via the A2A protocol for interoperability

## How It Works

The AI Tutor Agent uses a multi-agent system powered by CrewAI:

1. **Learning Gap Assessor Agent**: Analyzes the student's background and goals to identify knowledge gaps
2. **Learning Materials Designer Agent**: Creates personalized learning materials based on identified gaps

## Requirements

- Python 3.9+
- CrewAI library
- Google AI API key for Gemini model
- A2A protocol components (for server mode)

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Usage

### Standalone Client Mode

Run the interactive console application without A2A server:

```bash
python client.py
```

### A2A Server Mode

Run as an A2A protocol server:

```bash
python -m samples.python.agents.tutor --host localhost --port 10002
```

Or from within the module directory:

```bash
cd samples/python/agents/tutor
python __main__.py --host localhost --port 10002
```

## Input Format

The agent expects input in this format:

```
Topic: Machine Learning
Background: I have basic Python programming skills but no ML experience
Goals: To understand and implement basic ML algorithms
```

## Project Structure

- `tutor_agent.py`: Main agent implementation and tools
- `tutor_task_manager.py`: Task management for the agent
- `__main__.py`: A2A server entry point
- `client.py`: Standalone interactive client
- `requirements.txt`: Dependencies

## A2A Protocol Integration

This agent exposes the following capabilities via the A2A protocol:

- **Skill**: Learning Gap Assessment
- **Input Modes**: text/plain
- **Output Modes**: text/plain
- **Streaming**: Not supported
- **Model**: Google Gemini 1.5 Pro

## Extensibility

This agent can be extended in several ways:

- Add more specialized assessment tools
- Connect to real learning resource databases
- Integrate with learning management systems
- Support for more interaction formats (chat, voice, etc.)
- Add streaming capabilities to the A2A server

## License

MIT
