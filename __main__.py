"""This file serves as the main entry point for the Tutor Agent application.

It initializes the A2A server, defines the agent's capabilities,
and starts the server to handle incoming requests.
"""

from tutor_agent import TutorAgent
import click
from agent2agent.server import A2AServer
from agent2agent.types import AgentCapabilities, AgentCard, AgentSkill, MissingAPIKeyError
import logging
import os
from tutor_task_manager import TutorTaskManager
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", "host", default="localhost")
@click.option("--port", "port", default=10012)
def main(host, port):
    """Entry point for the A2A + CrewAI Tutor Agent sample."""
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise MissingAPIKeyError("GOOGLE_API_KEY environment variable not set.")

        capabilities = AgentCapabilities(streaming=False)
        skill = AgentSkill(
            id="learning_gap_assessment",
            name="Learning Gap Assessment",
            description=(
                "Assesses a student's current knowledge level and identifies "
                "specific learning gaps based on their background and goals. "
                "Creates personalized learning plans with tailored resources."
            ),
            tags=["education", "learning assessment", "personalized learning"],
            examples=[
                "Topic: Machine Learning, Background: Basic Python knowledge, Goals: Build ML models",
                "Topic: Spanish Language, Background: No prior experience, Goals: Basic conversation"
            ],
        )

        agent_card = AgentCard(
            name="AI Tutor Agent",
            description=(
                "An intelligent tutor that helps students understand their learning gaps "
                "and designs personalized learning materials based on topics of their choice."
            ),
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=TutorAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=TutorAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        server = A2AServer(
            agent_card=agent_card,
            task_manager=TutorTaskManager(agent=TutorAgent()),
            host=host,
            port=port,
        )
        logger.info(f"Starting server on {host}:{port}")
        server.start()
    except MissingAPIKeyError as e:
        logger.error(f"Error: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        exit(1)


if __name__ == "__main__":
    main() 