"""Tutor Agent Task Manager."""

import logging
from typing import AsyncIterable, Dict, Any, List
from tutor_agent import TutorAgent
from agent2agent.server.task_manager import InMemoryTaskManager
from agent2agent.server import utils
from agent2agent.types import (
    Artifact,
    JSONRPCResponse,
    SendTaskRequest,
    SendTaskResponse,
    SendTaskStreamingRequest,
    SendTaskStreamingResponse,
    Task,
    TaskSendParams,
    TaskState,
    TaskStatus,
    TextPart,
)

logger = logging.getLogger(__name__)

class TutorTaskManager(InMemoryTaskManager):
    """Tutor Task Manager handles task routing and response packing."""

    def __init__(self, agent: TutorAgent):
        super().__init__()
        self.agent = agent

    async def _stream_generator(
        self, request: SendTaskRequest
    ) -> AsyncIterable[SendTaskResponse]:
        raise NotImplementedError("Streaming is not supported by TutorAgent")

    async def on_send_task(
        self, request: SendTaskRequest
    ) -> SendTaskResponse | AsyncIterable[SendTaskResponse]:
        # Check if the output modes are compatible
        if not utils.are_modalities_compatible(
            request.params.acceptedOutputModes,
            TutorAgent.SUPPORTED_CONTENT_TYPES,
        ):
            logger.warning(
                "Unsupported output mode. Received %s, Support %s",
                request.params.acceptedOutputModes,
                TutorAgent.SUPPORTED_CONTENT_TYPES,
            )
            return utils.new_incompatible_types_error(request.id)

        task_send_params: TaskSendParams = request.params
        await self.upsert_task(task_send_params)

        return await self._invoke(request)

    async def on_send_task_subscribe(
        self, request: SendTaskStreamingRequest
    ) -> AsyncIterable[SendTaskStreamingResponse] | JSONRPCResponse:
        error = self._validate_request(request)
        if error:
            return error

        await self.upsert_task(request.params)
        # Streaming is not implemented
        raise NotImplementedError("Streaming is not supported by TutorAgent")

    async def _update_store(
        self, task_id: str, status: TaskStatus, artifacts: List[Artifact] = None
    ) -> Task:
        async with self.lock:
            try:
                task = self.tasks[task_id]
            except KeyError as exc:
                logger.error("Task %s not found for updating the task", task_id)
                raise ValueError(f"Task {task_id} not found") from exc

            task.status = status

            if status.message is not None:
                self.task_messages[task_id].append(status.message)

            if artifacts is not None:
                if task.artifacts is None:
                    task.artifacts = []
                task.artifacts.extend(artifacts)

            return task

    async def _invoke(self, request: SendTaskRequest) -> SendTaskResponse:
        task_send_params: TaskSendParams = request.params
        query = self._get_user_query(task_send_params)
        
        try:
            # Invoke the agent
            logger.info(f"Invoking tutor agent with query: {query}")
            result = self.agent.invoke(query, task_send_params.sessionId)
            
            # Format the response
            formatted_response = self.agent.get_formatted_response(result)
            
            # Create an artifact with the formatted response
            parts = [TextPart(text=formatted_response)]
            
            # Update the task status to completed with the artifact
            task = await self._update_store(
                task_send_params.id,
                TaskStatus(state=TaskState.COMPLETED),
                [Artifact(parts=parts)],
            )
            
            return SendTaskResponse(id=request.id, result=task)
            
        except Exception as e:
            logger.error(f"Error in tutor task: {e}", exc_info=True)
            
            # Update the task status to failed
            error_message = f"Error: {str(e)}"
            parts = [TextPart(text=error_message)]
            
            task = await self._update_store(
                task_send_params.id,
                TaskStatus(state=TaskState.FAILED),
                [Artifact(parts=parts)],
            )
            
            return SendTaskResponse(id=request.id, result=task)

    def _get_user_query(self, task_send_params: TaskSendParams) -> str:
        """Extract the user query from the task parameters."""
        if not task_send_params.message or not task_send_params.message.parts:
            return ""
            
        part = task_send_params.message.parts[0]
        if not isinstance(part, TextPart):
            raise ValueError("Only text parts are supported")

        return part.text 