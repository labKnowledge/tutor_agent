"""Tutor Agent based on CrewAI.

This agent helps students identify learning gaps and creates personalized learning materials.
"""

import os
from typing import Any, Dict, List, Optional
from uuid import uuid4
from dotenv import load_dotenv
from crewai import Agent, Crew, Task, Process
from crewai import LLM
from crewai.tools import tool
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class LearningGap(BaseModel):
    """Represents a learning gap identified by the tutor.
    
    Attributes:
        id: Unique identifier for the learning gap.
        topic: The main topic related to the gap.
        description: Detailed description of the gap.
        severity: How critical this gap is (1-5 scale).
        recommended_materials: List of recommended learning materials.
    """
    id: str
    topic: str
    description: str
    severity: int
    recommended_materials: List[str] = []

class LearningPlan(BaseModel):
    """Represents a personalized learning plan.
    
    Attributes:
        id: Unique identifier for the learning plan.
        student_level: Assessed level of the student.
        gaps: List of identified learning gaps.
        recommended_resources: Personalized learning resources.
        milestones: Key learning milestones to track progress.
        estimated_time: Estimated time to complete the plan (in hours).
    """
    id: str
    student_level: str
    gaps: List[LearningGap] = []
    recommended_resources: List[Dict[str, str]] = []
    milestones: List[str] = []
    estimated_time: int

def get_api_key() -> str:
    """Helper method to handle API Key."""
    load_dotenv()
    return os.getenv("GOOGLE_API_KEY")

@tool("AssessStudentTool")
def assess_student_tool(topic: str, student_background: str, student_goals: str) -> Dict[str, Any]:
    """Assesses student's current knowledge level and identifies learning gaps."""
    # In a real implementation, this might use specific assessment methods or connect to a knowledge base
    # For this example, we'll simulate the assessment process
    
    # Identify key areas in the topic that need assessment
    key_areas = f"Based on the topic '{topic}', the key areas to assess are: fundamentals, advanced concepts, practical applications"
    
    # Analyze student background for potential gaps
    analysis = f"Analysis of student background: {student_background}\n"
    analysis += f"Student goals: {student_goals}\n"
    
    # Create a detailed assessment
    assessment = {
        "assessed_level": "intermediate",  # This would be dynamically determined in a real system
        "identified_gaps": [
            LearningGap(
                id=uuid4().hex,
                topic=f"Fundamentals of {topic}",
                description=f"Gaps in basic understanding of {topic} fundamentals",
                severity=3,
                recommended_materials=["Basic tutorials", "Introductory courses"]
            ).dict(),
            LearningGap(
                id=uuid4().hex,
                topic=f"Advanced {topic} concepts",
                description=f"Limited knowledge of advanced {topic} principles",
                severity=4,
                recommended_materials=["Advanced courses", "Technical documentation"]
            ).dict()
        ]
    }
    
    return assessment

@tool("CreateLearningMaterialsTool")
def create_learning_materials_tool(topic: str, identified_gaps: List[Dict], student_level: str, student_goals: str) -> Dict[str, Any]:
    """Creates personalized learning materials based on identified gaps."""
    
    # In a real implementation, this would connect to a content database or generate materials
    # For this example, we'll simulate the creation process
    
    resources = []
    milestones = []
    
    # Create resources for each gap
    for gap in identified_gaps:
        # Create specific resources for this gap
        gap_resources = [
            {
                "title": f"Understanding {gap['topic']}",
                "type": "article",
                "difficulty": "beginner" if student_level == "beginner" else "intermediate",
                "url": f"https://example.com/learn/{gap['topic'].lower().replace(' ', '-')}"
            },
            {
                "title": f"Interactive {gap['topic']} Exercises",
                "type": "practice",
                "difficulty": student_level,
                "url": f"https://example.com/practice/{gap['topic'].lower().replace(' ', '-')}"
            }
        ]
        resources.extend(gap_resources)
        
        # Add milestone for this gap
        milestones.append(f"Master the basics of {gap['topic']}")
    
    # Add advanced resources based on student goals
    if "mastery" in student_goals.lower() or "advanced" in student_goals.lower():
        resources.append({
            "title": f"Advanced {topic} Masterclass",
            "type": "course",
            "difficulty": "advanced",
            "url": f"https://example.com/courses/advanced-{topic.lower().replace(' ', '-')}"
        })
        milestones.append(f"Complete advanced {topic} project")
    
    learning_plan = LearningPlan(
        id=uuid4().hex,
        student_level=student_level,
        gaps=[LearningGap(**gap) for gap in identified_gaps],
        recommended_resources=resources,
        milestones=milestones,
        estimated_time=20  # This would be dynamically calculated in a real system
    ).dict()
    
    return learning_plan

class TutorAgent:
    """Agent that assesses students and creates personalized learning materials."""

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        # Initialize the LLM using Gemini model with Google API key
        self.model = LLM(model="gemini/gemini-1.5-pro", api_key=get_api_key())

        # Create the assessor agent
        self.assessor_agent = Agent(
            role="Learning Gap Assessor",
            goal="Accurately identify a student's learning gaps based on their background and goals",
            backstory=(
                "You are an expert educator with years of experience in identifying learning gaps "
                "and assessing student knowledge levels. You can quickly pinpoint areas where a student "
                "needs additional support or education based on their background and goals."
            ),
            verbose=True,
            allow_delegation=False,
            tools=[assess_student_tool],
            llm=self.model,
        )

        # Create the learning materials creator agent
        self.materials_creator_agent = Agent(
            role="Learning Materials Designer",
            goal="Create personalized, effective learning materials to address identified learning gaps",
            backstory=(
                "You are a curriculum designer specializing in creating customized learning materials "
                "that address specific learning gaps. You excel at matching resources to a student's "
                "learning style, level, and goals to maximize their educational progress."
            ),
            verbose=True,
            allow_delegation=False,
            tools=[create_learning_materials_tool],
            llm=self.model,
        )

        # Define the assessment task
        self.assessment_task = Task(
            description=(
                "Analyze the student's information: topic of interest '{topic}', "
                "background '{student_background}', and goals '{student_goals}'. "
                "Use the AssessStudentTool to conduct a thorough assessment and identify learning gaps."
            ),
            expected_output="A detailed assessment of the student's learning gaps",
            agent=self.assessor_agent,
        )

        # Define the materials creation task
        self.materials_task = Task(
            description=(
                "Based on the assessment results, create personalized learning materials for the student. "
                "Topic: '{topic}', Identified gaps: {identified_gaps}, Student level: {student_level}, "
                "Student goals: '{student_goals}'. Use the CreateLearningMaterialsTool to generate "
                "a customized learning plan with appropriate resources and milestones."
            ),
            expected_output="A personalized learning plan with tailored resources and milestones",
            agent=self.materials_creator_agent,
        )

        # Create a crew with both agents
        self.tutor_crew = Crew(
            agents=[self.assessor_agent, self.materials_creator_agent],
            tasks=[self.assessment_task, self.materials_task],
            process=Process.sequential,
            verbose=True,
        )

    def parse_student_info(self, query: str) -> Dict[str, str]:
        """Extract student information from the query."""
        # This is a simple parser - in a real implementation, you might use more sophisticated methods
        lines = query.strip().split('\n')
        info = {
            "topic": "",
            "student_background": "",
            "student_goals": ""
        }
        
        for line in lines:
            if "topic:" in line.lower():
                info["topic"] = line.split(":", 1)[1].strip()
            elif "background:" in line.lower():
                info["student_background"] = line.split(":", 1)[1].strip()
            elif "goals:" in line.lower():
                info["student_goals"] = line.split(":", 1)[1].strip()
                
        return info

    def invoke(self, query: str, session_id: str) -> Dict[str, Any]:
        """Process the student query and generate a learning plan."""
        # Parse student information from the query
        student_info = self.parse_student_info(query)
        
        if not student_info["topic"]:
            return {"error": "Please specify a topic of interest."}
            
        # Provide defaults for missing information
        if not student_info["student_background"]:
            student_info["student_background"] = "No background information provided."
        if not student_info["student_goals"]:
            student_info["student_goals"] = "General knowledge improvement."
            
        logger.info(f"Processing request for topic: {student_info['topic']}")
            
        try:
            # Format the assessment task with the current inputs
            formatted_assessment_description = self.assessment_task.description.format(
                topic=student_info["topic"],
                student_background=student_info["student_background"],
                student_goals=student_info["student_goals"]
            )
            self.assessment_task.description = formatted_assessment_description
            
            # Simulate assessment data instead of directly calling the tool
            # In a real implementation, this would come from the crew execution results
            assessment_data = {
                "assessed_level": "intermediate",
                "identified_gaps": [
                    {
                        "id": uuid4().hex,
                        "topic": f"Fundamentals of {student_info['topic']}",
                        "description": f"Gaps in basic understanding of {student_info['topic']} fundamentals",
                        "severity": 3,
                        "recommended_materials": ["Basic tutorials", "Introductory courses"]
                    },
                    {
                        "id": uuid4().hex,
                        "topic": f"Advanced {student_info['topic']} concepts",
                        "description": f"Limited knowledge of advanced {student_info['topic']} principles",
                        "severity": 4,
                        "recommended_materials": ["Advanced courses", "Technical documentation"]
                    }
                ]
            }
            
            # Format the materials creation task
            formatted_materials_description = self.materials_task.description.format(
                topic=student_info["topic"],
                identified_gaps=assessment_data["identified_gaps"],
                student_level=assessment_data["assessed_level"],
                student_goals=student_info["student_goals"]
            )
            self.materials_task.description = formatted_materials_description
            
            # Execute the crew workflow
            try:
                crew_result = self.tutor_crew.kickoff()
                logger.info(f"Crew execution completed: {crew_result}")
            except Exception as crew_err:
                logger.warning(f"Crew execution failed, falling back to simulated data: {crew_err}")
                # Continue with simulated data if crew execution fails
            
            # Simulate learning plan data instead of directly calling the tool
            # In a real implementation, this would come from the crew execution results
            resources = []
            milestones = []
            
            # Create resources for each gap
            for gap in assessment_data["identified_gaps"]:
                gap_resources = [
                    {
                        "title": f"Understanding {gap['topic']}",
                        "type": "article",
                        "difficulty": "beginner" if assessment_data["assessed_level"] == "beginner" else "intermediate",
                        "url": f"https://example.com/learn/{gap['topic'].lower().replace(' ', '-')}"
                    },
                    {
                        "title": f"Interactive {gap['topic']} Exercises",
                        "type": "practice",
                        "difficulty": assessment_data["assessed_level"],
                        "url": f"https://example.com/practice/{gap['topic'].lower().replace(' ', '-')}"
                    }
                ]
                resources.extend(gap_resources)
                milestones.append(f"Master the basics of {gap['topic']}")
            
            # Add advanced resources based on student goals
            if "mastery" in student_info["student_goals"].lower() or "advanced" in student_info["student_goals"].lower():
                resources.append({
                    "title": f"Advanced {student_info['topic']} Masterclass",
                    "type": "course",
                    "difficulty": "advanced",
                    "url": f"https://example.com/courses/advanced-{student_info['topic'].lower().replace(' ', '-')}"
                })
                milestones.append(f"Complete advanced {student_info['topic']} project")
            
            learning_plan_data = {
                "id": uuid4().hex,
                "student_level": assessment_data["assessed_level"],
                "gaps": assessment_data["identified_gaps"],
                "recommended_resources": resources,
                "milestones": milestones,
                "estimated_time": 20
            }
            
            # Combine results
            result = {
                "assessment": assessment_data,
                "learning_plan": learning_plan_data,
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in tutor agent: {e}", exc_info=True)
            return {"error": f"Failed to generate learning plan: {str(e)}"}
            
    def get_formatted_response(self, result: Dict[str, Any]) -> str:
        """Format the result into a human-readable response."""
        if "error" in result:
            return f"Error: {result['error']}"
            
        assessment = result["assessment"]
        plan = result["learning_plan"]
        
        response = f"# Personalized Learning Plan\n\n"
        response += f"## Student Assessment\n"
        response += f"Current knowledge level: {assessment['assessed_level']}\n\n"
        
        response += f"## Identified Learning Gaps\n"
        for gap in assessment["identified_gaps"]:
            response += f"- {gap['topic']}: {gap['description']} (Severity: {gap['severity']}/5)\n"
        
        response += f"\n## Recommended Learning Resources\n"
        for resource in plan["recommended_resources"]:
            response += f"- [{resource['title']}]({resource['url']}) - {resource['type'].capitalize()}, {resource['difficulty']} level\n"
        
        response += f"\n## Learning Milestones\n"
        for i, milestone in enumerate(plan["milestones"], 1):
            response += f"{i}. {milestone}\n"
            
        response += f"\n## Estimated Time to Complete: {plan['estimated_time']} hours\n"
        
        return response 