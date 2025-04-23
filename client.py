"""Standalone client for interacting with the Tutor Agent."""

import asyncio
import logging
import sys
import uuid
from typing import Dict, Any

from tutor_agent import TutorAgent
from tutor_task_manager import TutorTaskManager, SendTaskRequest, Message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

async def process_request(request_text: str) -> str:
    """Process a student's request using the tutor agent."""
    # Initialize the agent and task manager
    agent = TutorAgent()
    task_manager = TutorTaskManager(agent)
    
    # Create a unique task ID
    task_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    
    # Format the message
    message = Message(
        parts=[{"type": "text", "text": request_text}],
        role="user"
    )
    
    # Create the request
    request = SendTaskRequest(
        id=task_id,
        params={
            "id": task_id,
            "sessionId": session_id,
            "message": message,
            "acceptedOutputModes": ["text", "text/plain"]
        }
    )
    
    # Process the request
    response = await task_manager.on_send_task(request)
    
    # Extract the response text from the artifacts
    if response.result.artifacts:
        artifact = response.result.artifacts[0]
        parts = artifact.get("parts", [])
        for part in parts:
            if part.get("type") == "text":
                return part.get("text", "No response generated.")
    
    return "No response generated."

async def interactive_session():
    """Run an interactive session with the tutor agent."""
    print("""
    ========================================
    Welcome to the AI Tutor Agent!
    ========================================
    
    This agent will help identify your learning gaps and create
    personalized learning plans for any topic of your choice.
    
    Please provide information in the following format:
    
    Topic: [Your topic of interest]
    Background: [Your current knowledge level and experience]
    Goals: [What you want to achieve by learning this topic]
    
    Type 'exit' to quit.
    ----------------------------------------
    """)
    
    while True:
        print("\nEnter your information (or type 'exit' to quit):")
        lines = []
        while True:
            line = input()
            if line.lower() == "exit":
                print("Thank you for using the AI Tutor Agent. Goodbye!")
                return
            if not line.strip():
                break
            lines.append(line)
        
        # Process the request if lines were entered
        if lines:
            request_text = "\n".join(lines)
            print("\nProcessing your request...\n")
            
            try:
                response = await process_request(request_text)
                print("\n" + response)
            except Exception as e:
                logger.error(f"Error processing request: {e}")
                print(f"\nAn error occurred: {str(e)}")

def main():
    """Main entry point of the client application."""
    try:
        asyncio.run(interactive_session())
    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main() 