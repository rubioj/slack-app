# Import required packages
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
import csv
from datetime import datetime
import re

def convert_mentions_to_names(text, client):
    """
    Convert user mentions in message text from IDs to real names.
    Args:
        text (str): Message text containing mentions
        client: Slack client instance
    Returns:
        str: Text with mentions converted to real names
    """
    # Find all user mentions in the text
    mention_pattern = re.compile(r'<@([A-Z0-9]+)>')
    mentions = mention_pattern.finditer(text)
    
    # Replace each mention with the user's real name
    new_text = text
    for match in mentions:
        user_id = match.group(1)
        try:
            user_info = client.users_info(user=user_id)["user"]
            real_name = user_info["real_name"]
            new_text = new_text.replace(f'<@{user_id}>', f'@{real_name}')
        except:
            # If we can't get user info, leave the mention as is
            continue
    
    return new_text

def get_channel_messages(channel_id):
    """
    Retrieve messages from a Slack channel and save them to a CSV file.
    Args:
        channel_id (str): The ID of the Slack channel to fetch messages from
    """
    try:
        # Initialize the Slack client with the bot token from environment variable
        client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
        
        # Create a timestamp-based filename for the CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"slack_messages_{timestamp}.csv"
        
        # Call the conversations.history method to fetch messages
        result = client.conversations_history(
            channel=channel_id,
            limit=20
        )
        
        # Check if any messages were returned
        if result["messages"]:
            # Open CSV file for writing
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                # Create CSV writer
                csvwriter = csv.writer(csvfile)
                
                # Write header row
                csvwriter.writerow(['Timestamp', 'Username', 'Message', 'Thread Replies'])
                
                # Iterate through messages in reverse order (oldest to newest)
                for message in reversed(result["messages"]):
                    # Get user info
                    try:
                        user_info = client.users_info(user=message["user"])["user"]
                        username = user_info["real_name"]
                    except:
                        username = "Unknown User"
                    
                    # Convert timestamp to readable format
                    timestamp = datetime.fromtimestamp(float(message["ts"])).strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Convert any user mentions in the message text to real names
                    message_text = convert_mentions_to_names(message["text"], client)
                    
                    # Check for thread replies
                    thread_count = message.get("reply_count", 0)
                    thread_status = f"{thread_count} replies" if thread_count > 0 else "No replies"
                    
                    # Write message to CSV
                    csvwriter.writerow([
                        timestamp,
                        username,
                        message_text,
                        thread_status
                    ])
                    
                    # Also print to console for verification
                 #   print(f"[{timestamp}] {username}: {message_text}")
            
            print(f"\nMessages have been saved to {csv_filename}")
                
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