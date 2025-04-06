from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os

def list_external_channels():
    try:
        # Initialize the Slack client with the bot token
        client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
        
        # Get the list of all conversations, including external shared channels
        result = client.conversations_list(
            types="public_channel,private_channel,mpim,im",
            exclude_archived=True
        )
        
        # Print each channel's details, highlighting external ones
        print("\nAvailable channels:")
        print("------------------")
        for channel in result["channels"]:
            is_shared = channel.get("is_shared", False)
            is_external = channel.get("is_ext_shared", False)
            
            if is_shared or is_external:
                print(f"Channel: #{channel['name']}")
                print(f"ID: {channel['id']}")
                print(f"Is External: {is_external}")
                print(f"Is Shared: {is_shared}")
                print("------------------")
            
    except SlackApiError as e:
        print(f"Error: {e.response['error']}")
        if "missing_scope" in str(e):
            print("\nMissing required scopes. Please add the following scopes to your bot:")
            print("- groups:history")
            print("- im:history")
            print("- mpim:history")
            print("- channels:read")
            print("- groups:read")
            print("- team:read")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if not os.environ.get("SLACK_BOT_TOKEN"):
        print("Error: SLACK_BOT_TOKEN environment variable is not set")
    else:
        list_external_channels() 