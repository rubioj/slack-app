from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os

def list_channels():
    try:
        # Initialize the Slack client with the bot token
        client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
        
        # Get the list of channels
        result = client.conversations_list(types="public_channel")
        
        # Print each channel's name and ID
        print("\nAvailable channels:")
        print("------------------")
        for channel in result["channels"]:
            print(f"Channel: #{channel['name']}")
            print(f"ID: {channel['id']}")
            print("------------------")
            
    except SlackApiError as e:
        print(f"Error: {e.response['error']}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if not os.environ.get("SLACK_BOT_TOKEN"):
        print("Error: SLACK_BOT_TOKEN environment variable is not set")
    else:
        list_channels() 