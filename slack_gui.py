import tkinter as tk
from tkinter import ttk, messagebox
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from datetime import datetime
import csv
import re
from dotenv import load_dotenv
import requests
from pathlib import Path

class SlackMessagesGUI:
    def __init__(self, root):
        # Load environment variables from .env file
        load_dotenv()
        
        # Get the token from environment
        self.slack_token = os.getenv('SLACK_BOT_TOKEN')
        if not self.slack_token:
            messagebox.showerror("Error", "SLACK_BOT_TOKEN not found in .env file")
            root.destroy()
            return
            
        self.root = root
        self.root.title("Slack Channel Exporter")
        self.root.geometry("500x300")
        
        # Configure style
        style = ttk.Style()
        style.configure('TButton', padding=5)
        style.configure('TLabel', padding=5)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Channel ID input
        ttk.Label(main_frame, text="Channel ID:").grid(row=0, column=0, sticky=tk.W)
        self.channel_var = tk.StringVar()
        self.channel_entry = ttk.Entry(main_frame, textvariable=self.channel_var, width=40)
        self.channel_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Number of messages/files input
        ttk.Label(main_frame, text="Number of items:").grid(row=1, column=0, sticky=tk.W)
        self.count_var = tk.StringVar(value="20")
        self.count_entry = ttk.Entry(main_frame, textvariable=self.count_var, width=10)
        self.count_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Create a frame for buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        # Export Messages button
        self.export_button = ttk.Button(button_frame, text="Export Messages", command=self.export_messages)
        self.export_button.grid(row=0, column=0, padx=5)
        
        # Download Files button
        self.download_button = ttk.Button(button_frame, text="Download Files", command=self.download_files)
        self.download_button.grid(row=0, column=1, padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            mode='indeterminate'
        )
        self.progress_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.progress_bar.grid_remove()
        
        # Status label
        self.status_var = tk.StringVar(value="")
        self.status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            justify=tk.CENTER
        )
        self.status_label.grid(row=4, column=0, columnspan=3, pady=5)
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def start_progress(self):
        """Show and start the progress bar animation"""
        self.progress_bar.grid()
        self.progress_bar.start(10)
        self.export_button.state(['disabled'])
        self.download_button.state(['disabled'])
        self.channel_entry.state(['disabled'])
        self.count_entry.state(['disabled'])

    def stop_progress(self):
        """Stop and hide the progress bar"""
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        self.export_button.state(['!disabled'])
        self.download_button.state(['!disabled'])
        self.channel_entry.state(['!disabled'])
        self.count_entry.state(['!disabled'])
        self.status_var.set("")

    def update_status(self, message):
        """Update status label"""
        self.status_var.set(message)
        self.root.update()

    def convert_mentions_to_names(self, text, client):
        """Convert user mentions in message text from IDs to real names."""
        mention_pattern = re.compile(r'<@([A-Z0-9]+)>')
        mentions = mention_pattern.finditer(text)
        
        new_text = text
        for match in mentions:
            user_id = match.group(1)
            try:
                user_info = client.users_info(user=user_id)["user"]
                real_name = user_info["real_name"]
                new_text = new_text.replace(f'<@{user_id}>', f'@{real_name}')
            except:
                continue
        
        return new_text

    def export_messages(self):
        """Export messages from Slack channel to CSV."""
        # Get channel ID and message count
        channel_id = self.channel_var.get().strip()
        try:
            msg_count = int(self.count_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of messages")
            return
        
        # Validate channel ID
        if not channel_id:
            messagebox.showerror("Error", "Please enter a channel ID")
            return
        
        try:
            # Start progress indication
            self.start_progress()
            self.update_status("Connecting to Slack...")
            
            # Initialize Slack client
            client = WebClient(token=self.slack_token)
            
            # Create timestamp-based filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"slack_messages_{timestamp}.csv"
            
            self.update_status("Fetching messages...")
            
            # Get messages
            result = client.conversations_history(
                channel=channel_id,
                limit=msg_count
            )
            
            if result["messages"]:
                self.update_status("Processing messages...")
                
                # Write to CSV
                with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerow(['Timestamp', 'Username', 'Message', 'Thread Replies'])
                    
                    for message in reversed(result["messages"]):
                        # Get user info
                        try:
                            user_info = client.users_info(user=message["user"])["user"]
                            username = user_info["real_name"]
                        except:
                            username = "Unknown User"
                        
                        # Convert timestamp
                        timestamp = datetime.fromtimestamp(float(message["ts"])).strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Convert mentions
                        message_text = self.convert_mentions_to_names(message["text"], client)
                        
                        # Get thread info
                        thread_count = message.get("reply_count", 0)
                        thread_status = f"{thread_count} replies" if thread_count > 0 else "No replies"
                        
                        # Write to CSV
                        csvwriter.writerow([
                            timestamp,
                            username,
                            message_text,
                            thread_status
                        ])
                
                self.stop_progress()
                messagebox.showinfo("Success", f"Messages exported to {csv_filename}")
            else:
                self.stop_progress()
                messagebox.showinfo("Info", "No messages found in the channel.")
                
        except SlackApiError as e:
            self.stop_progress()
            error_message = f"Slack API Error: {e.response['error']}"
            messagebox.showerror("Error", error_message)
        except Exception as e:
            self.stop_progress()
            error_message = f"An error occurred: {str(e)}"
            messagebox.showerror("Error", error_message)

    def download_files(self):
        """Download files shared in the Slack channel"""
        channel_id = self.channel_var.get().strip()
        try:
            limit = int(self.count_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
            return
        
        if not channel_id:
            messagebox.showerror("Error", "Please enter a channel ID")
            return
        
        try:
            self.start_progress()
            self.update_status("Connecting to Slack...")
            
            client = WebClient(token=self.slack_token)
            
            # Create downloads directory if it doesn't exist
            downloads_dir = Path("slack_downloads")
            downloads_dir.mkdir(exist_ok=True)
            
            # Get channel history
            self.update_status("Fetching channel history...")
            result = client.conversations_history(
                channel=channel_id,
                limit=limit
            )
            
            if not result["messages"]:
                self.stop_progress()
                messagebox.showinfo("Info", "No messages found in the channel.")
                return
            
            # Track downloaded files
            downloaded_files = []
            
            # Process messages
            for message in result["messages"]:
                if "files" in message:
                    for file in message["files"]:
                        try:
                            # Get file info
                            file_name = file.get("name", "unknown_file")
                            file_url = file.get("url_private_download") or file.get("url_private")
                            
                            if file_url:
                                self.update_status(f"Downloading: {file_name}")
                                
                                # Download file
                                response = requests.get(
                                    file_url,
                                    headers={"Authorization": f"Bearer {self.slack_token}"},
                                    stream=True
                                )
                                response.raise_for_status()
                                
                                # Save file
                                file_path = downloads_dir / file_name
                                with open(file_path, 'wb') as f:
                                    for chunk in response.iter_content(chunk_size=8192):
                                        if chunk:
                                            f.write(chunk)
                                
                                downloaded_files.append(file_name)
                                
                        except Exception as e:
                            print(f"Error downloading {file_name}: {str(e)}")
            
            self.stop_progress()
            
            if downloaded_files:
                message = f"Downloaded {len(downloaded_files)} files to {downloads_dir}"
                messagebox.showinfo("Success", message)
            else:
                messagebox.showinfo("Info", "No files found in the recent messages.")
                
        except SlackApiError as e:
            self.stop_progress()
            error_message = f"Slack API Error: {e.response['error']}"
            messagebox.showerror("Error", error_message)
        except Exception as e:
            self.stop_progress()
            error_message = f"An error occurred: {str(e)}"
            messagebox.showerror("Error", error_message)

def main():
    root = tk.Tk()
    app = SlackMessagesGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 