"""
Slack Bot integration for the Personal Assistant Agent.
Allows interaction with the agent through Slack.
"""

import os
import re
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from agent import PersonalAssistantAgent

# Load environment variables
load_dotenv()


class PersonalAssistantSlackBot:
    """
    Slack bot that integrates the Personal Assistant Agent.
    """

    def __init__(self):
        """
        Initialize the Slack bot.
        """
        # Get Slack tokens from environment
        self.bot_token = os.getenv('SLACK_BOT_TOKEN')
        self.app_token = os.getenv('SLACK_APP_TOKEN')

        if not self.bot_token or not self.app_token:
            raise ValueError("SLACK_BOT_TOKEN and SLACK_APP_TOKEN must be set")

        # Initialize Slack app
        self.app = App(token=self.bot_token)

        # Initialize the personal assistant agent
        self.agent = PersonalAssistantAgent()

        # Store conversation context per user
        self.user_contexts: Dict[str, list] = {}

        # Register event handlers
        self._register_handlers()

    def _register_handlers(self):
        """
        Register Slack event handlers.
        """
        # Handle app mentions
        @self.app.event("app_mention")
        def handle_mention(event, say, logger):
            asyncio.run(self._handle_mention_async(event, say, logger))

        # Handle direct messages
        @self.app.event("message")
        def handle_message(event, say, logger):
            # Ignore bot messages and threaded replies (unless it's a reply to the bot)
            if event.get("subtype") or event.get("bot_id"):
                return

            asyncio.run(self._handle_message_async(event, say, logger))

        # Handle slash command for quick actions
        @self.app.command("/assistant")
        def handle_assistant_command(ack, command, say, logger):
            ack()
            asyncio.run(self._handle_command_async(command, say, logger))

    async def _handle_mention_async(self, event, say, logger):
        """
        Handle app mentions asynchronously.

        Args:
            event: Slack event data
            say: Function to send messages
            logger: Logger instance
        """
        try:
            # Get the message text and remove the bot mention
            text = event.get("text", "")
            user_id = event.get("user")
            channel_id = event.get("channel")

            # Remove bot mention from text
            clean_text = re.sub(r'<@[A-Z0-9]+>', '', text).strip()

            if not clean_text:
                say("Hi! How can I assist you today?")
                return

            # Send typing indicator
            say(text="Processing your request...", thread_ts=event.get("ts"))

            # Get response from agent
            response = await self.agent.simple_query(clean_text)

            # Send response
            say(text=response, thread_ts=event.get("ts"))

        except Exception as e:
            logger.error(f"Error handling mention: {str(e)}")
            say(text=f"Sorry, I encountered an error: {str(e)}", thread_ts=event.get("ts"))

    async def _handle_message_async(self, event, say, logger):
        """
        Handle direct messages asynchronously.

        Args:
            event: Slack event data
            say: Function to send messages
            logger: Logger instance
        """
        try:
            # Only respond to direct messages (channel type is 'im')
            if event.get("channel_type") != "im":
                return

            text = event.get("text", "")
            user_id = event.get("user")

            if not text:
                return

            # Get response from agent
            response = await self.agent.simple_query(text)

            # Send response
            say(response)

        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            say(f"Sorry, I encountered an error: {str(e)}")

    async def _handle_command_async(self, command, say, logger):
        """
        Handle slash commands asynchronously.

        Args:
            command: Slack command data
            say: Function to send messages
            logger: Logger instance
        """
        try:
            command_text = command.get("text", "").strip()

            if not command_text:
                say({
                    "text": "Personal Assistant Commands",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "*Available commands:*\n"
                                        "• `/assistant emails` - Check recent unread emails\n"
                                        "• `/assistant calendar` - View upcoming events\n"
                                        "• `/assistant schedule [details]` - Schedule a new event\n"
                                        "• `/assistant [question]` - Ask any question"
                            }
                        }
                    ]
                })
                return

            # Handle specific commands
            if command_text.lower() == "emails":
                result = await self.agent.read_recent_emails(max_results=5, query='is:unread')

                if result['status'] == 'success' and result['count'] > 0:
                    emails = result['emails']
                    email_list = "\n".join([
                        f"• *{email['subject']}* from {email['from']}"
                        for email in emails
                    ])
                    say(f"You have {result['count']} unread emails:\n{email_list}")
                else:
                    say("No unread emails found or unable to access Gmail.")

            elif command_text.lower() == "calendar":
                result = await self.agent.get_calendar_events(max_results=5)

                if result['status'] == 'success' and result['count'] > 0:
                    events = result['events']
                    event_list = "\n".join([
                        f"• *{event['summary']}* - {event['start']}"
                        for event in events
                    ])
                    say(f"Upcoming events:\n{event_list}")
                else:
                    say("No upcoming events found or unable to access Calendar.")

            else:
                # General query
                response = await self.agent.simple_query(command_text)
                say(response)

        except Exception as e:
            logger.error(f"Error handling command: {str(e)}")
            say(f"Sorry, I encountered an error: {str(e)}")

    def start(self):
        """
        Start the Slack bot using Socket Mode.
        """
        handler = SocketModeHandler(self.app, self.app_token)
        print("Personal Assistant Slack Bot is running!")
        handler.start()


def main():
    """
    Main entry point for the Slack bot.
    """
    try:
        bot = PersonalAssistantSlackBot()
        bot.start()
    except ValueError as e:
        print(f"Configuration error: {str(e)}")
        print("\nMake sure the following environment variables are set:")
        print("  - SLACK_BOT_TOKEN")
        print("  - SLACK_APP_TOKEN")
        print("  - ANTHROPIC_API_KEY")
    except Exception as e:
        print(f"Error starting bot: {str(e)}")


if __name__ == "__main__":
    main()
