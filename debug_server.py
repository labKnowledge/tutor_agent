"""Debug script for the A2A Tutor Agent server.

This adds additional logging to help diagnose server issues.
"""

import logging
import sys
import os
from dotenv import load_dotenv
from tutor_agent import TutorAgent
import click
from common.server import A2AServer
from common.types import AgentCapabilities, AgentCard, AgentSkill, MissingAPIKeyError
from tutor_task_manager import TutorTaskManager

# Set up verbose logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for maximum verbosity
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Get logger instance
logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", "host", default="localhost")
@click.option("--port", "port", default=10012)
@click.option("--debug", "debug", is_flag=True, default=True, help="Enable debug logging")
def main(host, port, debug):
    """Debug entry point for the A2A + CrewAI Tutor Agent sample."""
    try:
        # Print environment variables (excluding sensitive data)
        env_vars = {k: "***" if "API_KEY" in k or "SECRET" in k or "TOKEN" in k else v 
                    for k, v in os.environ.items()}
        logger.debug(f"Environment variables: {env_vars}")
        
        load_dotenv()
        
        # Load API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY environment variable not set")
            raise MissingAPIKeyError("GOOGLE_API_KEY environment variable not set.")
        logger.debug("GOOGLE_API_KEY found in environment")
        
        logger.info(f"Starting debug server on {host}:{port}")
        
        # Create capabilities
        capabilities = AgentCapabilities(streaming=False)
        logger.debug(f"Created capabilities: {capabilities}")
        
        # Create skill
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
        logger.debug(f"Created skill: {skill}")
        
        # Create agent card
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
        logger.debug(f"Created agent card: {agent_card}")
        
        # Create task manager and agent
        logger.info("Initializing TutorAgent")
        agent = TutorAgent()
        logger.debug("TutorAgent initialized")
        
        logger.info("Initializing TaskManager")
        task_manager = TutorTaskManager(agent=agent)
        logger.debug("TaskManager initialized")
        
        # Create server
        logger.info("Creating A2A Server")
        server = A2AServer(
            agent_card=agent_card,
            task_manager=task_manager,
            host=host,
            port=port,
        )
        logger.debug("A2A Server created")
        
        # Start server
        logger.info(f"Starting server on {host}:{port}")
        server.start()
    except MissingAPIKeyError as e:
        logger.error(f"API Key Error: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}", exc_info=True)
        exit(1)


if __name__ == "__main__":
    main() 