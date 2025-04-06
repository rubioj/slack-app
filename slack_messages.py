# Import required packages
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os

def get_channel_messages(channel_id):
    """
    Retrieve and format the latest messages from a Slack channel.
    Args:
        channel_id (str): The ID of the Slack channel to fetch messages from
    """
    try:
        # Initialize the Slack client with the bot token from environment variable
        client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
        
        # Call the conversations.history method to fetch messages
        # Limit to 20 messages as per requirements
        result = client.conversations_history(
            channel=channel_id,
            limit=20
        )
        
        # Check if any messages were returned
        if result["messages"]:
            # Iterate through messages in reverse order (oldest to newest)
            for message in (result["messages"]):
                # Get the user info for the message sender
                user_info = client.users_info(user=message["user"])["user"]
                username = user_info["real_name"]
                
                # Format and print each message
                print(f"[{username}] {message['text']}")
                
        else:
            print("No messages found in the channel.")
            
    except SlackApiError as e:
        # Handle any errors that occur during API calls
        print(f"Error: {e.response['error']}")
    except Exception as e:
        # Handle any other unexpected errors
        print(f"An error occurred: {str(e)}")

def main():
    # Replace this with your channel ID
    CHANNEL_ID = "C03UNACE202"
    
    # Check if the SLACK_BOT_TOKEN environment variable is set
    if not os.environ.get("SLACK_BOT_TOKEN"):
        print("Error: SLACK_BOT_TOKEN environment variable is not set")
        return
    
    # Call the function to get and display messages
    get_channel_messages(CHANNEL_ID)

if __name__ == "__main__":
    main() 