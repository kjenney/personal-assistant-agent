# Personal Assistant Agent

A powerful personal assistant agent built with Claude's Agent SDK that helps you manage emails, schedule meetings, and search the web. Interact with it directly via Python or through Slack!

## Features

- **Email Management**: Read and filter Gmail emails
- **Calendar Management**: View upcoming events and create new calendar entries
- **Web Search**: Access current information from the web (via Claude's built-in capabilities)
- **Slack Integration**: Interact with your assistant directly in Slack
- **Natural Language Processing**: Powered by Claude Sonnet 4.5 for intelligent responses

## Architecture

- **Claude Agent SDK**: Core AI agent framework
- **Google APIs**: Gmail and Calendar integration
- **Slack Bolt**: Real-time Slack bot functionality
- **Python 3.10+**: Modern async/await support

## Prerequisites

- Python 3.10 or higher
- Node.js (required by Claude Agent SDK)
- Claude Code CLI installed: `npm install -g @anthropic-ai/claude-code`
- Anthropic API key
- Google Cloud project (for Gmail/Calendar access)
- Slack workspace (for Slack integration)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd personal-assistant-agent
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```bash
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
```

### 4. Set Up Google API Credentials

#### Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API and Google Calendar API
4. Go to "Credentials" and create OAuth 2.0 credentials
5. Download the credentials file and save it as `credentials.json` in the project root

#### Authorize the Application

When you first run the agent, it will open a browser window to authorize access to your Gmail and Google Calendar. After authorization, tokens will be saved locally for future use.

### 5. Set Up Slack App (Optional)

If you want to use the Slack integration:

1. Go to [Slack API](https://api.slack.com/apps)
2. Create a new app or select an existing one
3. Enable Socket Mode in "Socket Mode" settings
4. Create an App-Level Token with `connections:write` scope
5. Add Bot Token Scopes in "OAuth & Permissions":
   - `app_mentions:read`
   - `chat:write`
   - `im:history`
   - `im:read`
   - `im:write`
6. Install the app to your workspace
7. Copy the Bot Token and App Token to your `.env` file

## Usage

### Using the Agent Directly (Python)

Run the agent standalone:

```bash
python agent.py
```

Or use it programmatically:

```python
import anyio
from agent import PersonalAssistantAgent

async def main():
    agent = PersonalAssistantAgent()

    # Ask a question
    response = await agent.simple_query("What's on my calendar today?")
    print(response)

    # Read emails
    emails = await agent.read_recent_emails(max_results=5, query='is:unread')
    print(f"Found {emails['count']} unread emails")

    # Create a calendar event
    result = await agent.schedule_event(
        summary="Team Meeting",
        start_time="2025-10-25T10:00:00Z",
        end_time="2025-10-25T11:00:00Z",
        description="Weekly sync",
        attendees=["colleague@example.com"]
    )
    print(f"Event created: {result}")

anyio.run(main)
```

### Using the Slack Bot

Start the Slack bot:

```bash
python slack_bot.py
```

Once running, you can interact with the bot in several ways:

#### 1. Direct Messages

Send a direct message to the bot:

```
What emails do I have from John?
```

#### 2. Mentions in Channels

Mention the bot in any channel:

```
@PersonalAssistant what's on my calendar tomorrow?
```

#### 3. Slash Commands

Use the `/assistant` command:

```
/assistant emails          - Check recent unread emails
/assistant calendar        - View upcoming events
/assistant [question]      - Ask any question
```

## Example Interactions

### Email Management

```
You: "Show me unread emails from the last 24 hours"
Agent: "You have 3 unread emails:
• Project Update from john@company.com
• Meeting Invitation from sarah@company.com
• Monthly Report from reports@company.com"
```

### Calendar Management

```
You: "What's on my schedule tomorrow?"
Agent: "You have 2 events tomorrow:
• Team Standup at 9:00 AM
• Client Call at 2:00 PM"
```

### Scheduling

```
You: "Schedule a meeting with Jane tomorrow at 3 PM for 1 hour about the Q4 planning"
Agent: "I've created a calendar event:
• Title: Q4 Planning Meeting
• Time: Tomorrow at 3:00 PM - 4:00 PM
• Attendee: jane@company.com
Would you like me to add any additional details?"
```

### Web Search

```
You: "What's the latest news on AI agents?"
Agent: [Provides current information from web search]
```

## Project Structure

```
personal-assistant-agent/
├── agent.py              # Core agent implementation
├── slack_bot.py          # Slack bot integration
├── tools.py              # Custom tools for email/calendar
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── CLAUDE.md             # Project instructions
└── README.md             # This file
```

## Customization

### Adding Custom Tools

Edit `tools.py` to add new tools:

```python
async def my_custom_tool(param: str) -> Dict[str, Any]:
    """Your custom tool implementation"""
    return {"status": "success", "result": "..."}

# Add to TOOLS list
TOOLS.append({
    "name": "my_custom_tool",
    "description": "What this tool does",
    "input_schema": {...},
    "function": my_custom_tool
})
```

### Modifying Agent Behavior

Edit the `system_prompt` in `agent.py` to change how the agent behaves:

```python
self.system_prompt = """Your custom instructions here..."""
```

## Troubleshooting

### Authentication Errors

- Ensure your `ANTHROPIC_API_KEY` is valid
- Check that Google API credentials are properly set up
- Verify Slack tokens are correct and have the right scopes

### Import Errors

- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version: `python --version` (should be 3.10+)
- Check that Claude Code is installed: `npm list -g @anthropic-ai/claude-code`

### Google API Issues

- Ensure Gmail API and Calendar API are enabled in Google Cloud Console
- Check that `credentials.json` is in the project root
- Delete token files and re-authorize if needed

### Slack Connection Issues

- Verify Socket Mode is enabled in Slack app settings
- Check that all required OAuth scopes are added
- Ensure the app is installed in your workspace

## Security Considerations

- Never commit `.env`, `credentials.json`, or token files to version control
- Rotate API keys regularly
- Use least-privilege OAuth scopes
- Store credentials securely

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT

## Support

For issues related to:
- Claude Agent SDK: Check [official documentation](https://docs.claude.com/en/api/agent-sdk/overview)
- Google APIs: See [Google API Python Client](https://github.com/googleapis/google-api-python-client)
- Slack Integration: Visit [Slack API docs](https://api.slack.com/)

## Acknowledgments

Built with:
- [Claude Agent SDK](https://docs.claude.com/en/api/agent-sdk/overview) by Anthropic
- [Slack Bolt for Python](https://slack.dev/bolt-python/)
- [Google API Python Client](https://github.com/googleapis/google-api-python-client)