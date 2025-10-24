"""
Personal Assistant Agent using Claude Agent SDK.
Provides email reading, calendar management, and web search capabilities.
"""

import os
import anyio
from typing import AsyncIterator, Dict, Any, Optional
from dotenv import load_dotenv
from claude_agent_sdk import query, ClaudeSDKClient
from tools import read_emails, list_calendar_events, create_calendar_event, TOOLS


# Load environment variables
load_dotenv()


class PersonalAssistantAgent:
    """
    Personal Assistant Agent with email, calendar, and web search capabilities.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Personal Assistant Agent.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set")

        # System prompt defining the agent's role
        self.system_prompt = """You are a helpful personal assistant with the following capabilities:

1. Email Management:
   - Read emails from Gmail
   - Filter emails by various criteria (unread, sender, etc.)
   - Summarize email contents

2. Calendar Management:
   - View upcoming calendar events
   - Create new calendar events
   - Schedule meetings with attendees

3. Web Search:
   - Search for current information on the web
   - Provide up-to-date answers to questions

Your goal is to help the user manage their schedule and communications efficiently.
Be proactive, concise, and helpful. When scheduling meetings, always confirm details
like time, duration, and attendees before creating events.

Always provide clear summaries and actionable insights from emails and calendar events."""

    async def simple_query(self, prompt: str) -> str:
        """
        Send a simple query to the agent and get a response.

        Args:
            prompt: User's question or request

        Returns:
            Agent's response as a string
        """
        response_parts = []

        async for message in query(
            prompt=prompt,
            system=self.system_prompt,
            api_key=self.api_key
        ):
            response_parts.append(str(message))

        return ''.join(response_parts)

    async def interactive_query(self, prompt: str, conversation_history: list = None) -> AsyncIterator[str]:
        """
        Send an interactive query that can use custom tools.

        Args:
            prompt: User's question or request
            conversation_history: Previous conversation messages

        Yields:
            Response chunks from the agent
        """
        # For now, using the simple query approach
        # In a more advanced implementation, we'd use ClaudeSDKClient for bidirectional communication
        response = await self.simple_query(prompt)
        yield response

    def register_custom_tools(self):
        """
        Register custom tools with the agent.
        This would be used with ClaudeSDKClient for more advanced integrations.
        """
        return TOOLS

    async def read_recent_emails(self, max_results: int = 10, query: str = '') -> Dict[str, Any]:
        """
        Convenience method to read emails directly.

        Args:
            max_results: Maximum number of emails to retrieve
            query: Gmail search query

        Returns:
            Dictionary with email data
        """
        return await read_emails(max_results, query)

    async def get_calendar_events(self, max_results: int = 10) -> Dict[str, Any]:
        """
        Convenience method to get calendar events directly.

        Args:
            max_results: Maximum number of events to retrieve

        Returns:
            Dictionary with calendar events
        """
        return await list_calendar_events(max_results)

    async def schedule_event(
        self,
        summary: str,
        start_time: str,
        end_time: str,
        description: str = '',
        location: str = '',
        attendees: list = None
    ) -> Dict[str, Any]:
        """
        Convenience method to create a calendar event directly.

        Args:
            summary: Event title
            start_time: Start time in ISO format
            end_time: End time in ISO format
            description: Event description
            location: Event location
            attendees: List of attendee emails

        Returns:
            Dictionary with creation status
        """
        return await create_calendar_event(
            summary, start_time, end_time, description, location, attendees
        )


async def main():
    """
    Example usage of the Personal Assistant Agent.
    """
    try:
        agent = PersonalAssistantAgent()

        print("Personal Assistant Agent initialized successfully!")
        print("\nExample: Asking a simple question...")

        response = await agent.simple_query(
            "What's the weather like today and should I bring an umbrella?"
        )

        print(f"\nAgent Response:\n{response}")

        # Example: Reading emails (requires Google API setup)
        # print("\n\nChecking recent emails...")
        # emails = await agent.read_recent_emails(max_results=5, query='is:unread')
        # print(f"Found {emails.get('count', 0)} unread emails")

    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nMake sure ANTHROPIC_API_KEY is set in your environment or .env file")


if __name__ == "__main__":
    anyio.run(main)
