#!/bin/bash
# Test script for the A2A server API

# First test the agent card endpoint
echo "Testing agent card endpoint..."
curl -s http://localhost:10012/.well-known/agent.json | jq

# Then test the tasks/send endpoint
echo "Testing tasks/send endpoint..."
curl -X POST \
  http://localhost:10012/rpc \
  -H "Content-Type: application/json" \
  -d '{
  "jsonrpc": "2.0",
  "id": "request-1",
  "method": "tasks/send",
  "params": {
    "id": "task-123",
    "sessionId": "session-456",
    "acceptedOutputModes": ["text/plain"],
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "Topic: Machine Learning\nBackground: I have basic Python programming skills but no ML experience\nGoals: To understand and implement basic ML algorithms"
        }
      ]
    }
  }
}' | jq

echo "Test complete." 