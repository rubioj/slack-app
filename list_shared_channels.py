from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os

def list_shared_channels():
    try:
        # Initialize the Slack client with the bot token
        client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
        
        # Get all conversations the bot can see
        result = client.conversations_list(
            types="public_channel,private_channel",
            exclude_archived=True
        )
        
        print("\nSearching for shared/external channels...")
        found_shared = False
        
        for channel in result["channels"]:
            # Try to get more details about the channel
            try:
                channel_info = client.conversations_info(channel=channel["id"])["channel"]
                is_shared = channel_info.get("is_shared", False)
                is_external = channel_info.get("is_ext_shared", False)
                
                if is_shared or is_external:
                    found_shared = True
                    print("\n------------------")
                    print(f"Channel Name: #{channel['name']}")
                    print(f"Channel ID: {channel['id']}")
                    print(f"Is External Shared: {is_external}")
                    print(f"Is Shared: {is_shared}")
                    print("------------------")
            
            except SlackApiError as e:
                if "not_in_channel" not in str(e):
                    print(f"Error getting info for #{channel['name']}: {e.response['error']}")
        
        if not found_shared:
            print("\nNo shared or external channels found that the bot can access.")
            print("Make sure the bot is invited to the external channels you want to monitor.")
            
    except SlackApiError as e:
        print(f"\nError: {e.response['error']}")
        print("\nPlease verify these scopes are added to your bot:")
        print("- channels:read")
        print("- groups:read")
        print("- channels:history")
        print("- groups:history")
        print("\nAfter adding scopes:")
        print("1. Click 'Reinstall App' on the OAuth page")
        print("2. Update your SLACK_BOT_TOKEN environment variable with the new token")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    if not os.environ.get("SLACK_BOT_TOKEN"):
        print("Error: SLACK_BOT_TOKEN environment variable is not set")
    else:
        list_shared_channels() 