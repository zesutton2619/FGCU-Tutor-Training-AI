import sqlite3
import json
from openai import OpenAI
from dotenv import load_dotenv
import time
import os
import datetime
import random

load_dotenv()


class Backend:
    def __init__(self):
        OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.db_path = os.getenv("SQLITE_DB_PATH")  # Path to SQLite database file
        self.global_conversation_name = ''
        self.global_user_id = 0
        self.global_subject = ''
        self.global_mode = ''
        self.tutee_assistant_ids = {
            'Writing': 'asst_xqPTYqajw69DTFS2yidhYVBJ',
            'Chemistry': 'asst_M2fmEombFqQpmZHUmUBgkfVJ',
            'Biology': 'asst_A3KVHx9Rp7oM8l585JUAEbIU',
            'Physics': 'asst_2cDZXQUhhR9nvH93rx5dhTG8',
            'Nursing': 'asst_SCNZeLiWbJ1XmkLM9GTINtPV',
            'Math': 'asst_cPu94bL3l0kzcPaExKM270Cx',
            'Business': 'asst_ySOkMWNC06ql3weCpYQN1Pdi'
        }
        self.initialize_database()

    def initialize_database(self):
        # Create database tables if they don't exist
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS Conversations (
                        _id INTEGER PRIMARY KEY AUTOINCREMENT,
                        thread_id TEXT,
                        user_id INTEGER,
                        username TEXT,
                        subject TEXT,
                        mode TEXT,
                        conversation_name TEXT,
                        user_messages TEXT,
                        assistant_messages TEXT
                     )''')
        c.execute('''CREATE TABLE IF NOT EXISTS User_ID (
                            user_id INTEGER PRIMARY KEY,
                            username TEXT
                         )''')
        conn.commit()
        conn.close()

    def generate_user_id(self):
        self.global_user_id = random.randint(100, 999)
        return self.global_user_id

    def create_conversation_name(self):
        # Find the maximum conversation number among existing conversations for the current user
        max_conversation_number = 0
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''SELECT conversation_name FROM Conversations WHERE user_id = ?''', (self.global_user_id,))
        existing_conversations = c.fetchall()
        for conversation_tuple in existing_conversations:
            conversation_name = conversation_tuple[0]  # Extract conversation name from tuple
            if conversation_name and conversation_name.startswith(
                    f"{self.global_subject} {self.global_mode} Conversation "):
                conversation_number = int(conversation_name.split(" ")[-1])
                max_conversation_number = max(max_conversation_number, conversation_number)

        # Increment the maximum conversation number to generate the next conversation name
        new_conversation_number = max_conversation_number + 1
        self.global_conversation_name = (f"{self.global_subject} {self.global_mode} "
                                         f"Conversation {new_conversation_number}")
        print(self.global_conversation_name)
        return self.global_conversation_name

    def get_user_id(self):
        return self.global_user_id

    def get_conversation_name(self):
        return self.global_conversation_name

    def check_username(self, username):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''SELECT user_id FROM User_ID WHERE username = ?''', (username,))
        user_data = c.fetchone()
        if user_data:
            self.global_user_id = user_data[0]
            return self.global_user_id
        else:
            self.global_user_id = self.generate_user_id()
            c.execute('''INSERT INTO User_ID (user_id, username) VALUES (?, ?)''', (self.global_user_id, username))
            conn.commit()
            conn.close()
            return self.global_user_id

    def set_subject(self, subject_name):
        self.global_subject = subject_name

    def set_mode(self, mode):
        self.global_mode = mode

    def check_if_thread_exists(self, user_id, conversation_name):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''SELECT thread_id FROM Conversations 
                     WHERE user_id = ? AND conversation_name = ?''', (user_id, conversation_name))
        thread = c.fetchone()
        conn.close()
        return thread[0] if thread else None

    def generate_response(self, message_body, user_id, name, conversation_name):
        thread_id = self.check_if_thread_exists(user_id, conversation_name)

        if thread_id is None:
            print(f"Creating new thread for {name} with user_id {user_id}")
            thread = self.client.beta.threads.create()
            thread_id = thread.id
        else:
            print(f"Retrieving existing thread for {name} with wa_id {user_id}")
            thread = self.client.beta.threads.retrieve(thread_id)

        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message_body,
        )

        new_message = self.run_assistant(thread, user_id, name, conversation_name)
        print("Current conversation: ", conversation_name)
        print(f"To {name}:", new_message)
        return new_message

    def run_assistant(self, thread, user_id, name, conversation_name):
        if self.global_mode == 'Tutee':
            assistant_id = self.tutee_assistant_ids[self.global_subject]
        elif self.global_mode == 'Tutor':
            assistant_id = 'asst_8beVxeg82dDaJ1jUaP8tDy4n'
        else:
            assistant_id = 'asst_8beVxeg82dDaJ1jUaP8tDy4n'
        print("Mode:", self.global_mode, "Assistant:", assistant_id)
        assistant = self.client.beta.assistants.retrieve(f"{assistant_id}")

        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

        while run.status != "completed":
            time.sleep(0.5)
            run = self.client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        messages = self.client.beta.threads.messages.list(thread_id=thread.id)
        new_message = messages.data[0].content[0].text.value
        self.store_conversation(thread, messages, user_id, name, conversation_name)
        return new_message

    def store_conversation(self, thread, conversation, user_id, name, conversation_name):
        thread_id = thread.id
        user_messages = []
        assistant_messages = []
        for message in conversation.data:
            if message.role == "user":
                user_messages.append({
                    "content": message.content[0].text.value,
                    "timestamp": message.created_at
                })
            elif message.role == "assistant":
                assistant_messages.append({
                    "content": message.content[0].text.value,
                    "timestamp": message.created_at
                })

        # Convert user_messages and assistant_messages to JSON strings
        user_messages_json = json.dumps(user_messages)
        assistant_messages_json = json.dumps(assistant_messages)

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Check if a conversation with the same thread_id exists
        c.execute('''SELECT * FROM Conversations WHERE thread_id = ?''', (thread_id,))
        existing_conversation = c.fetchone()

        if existing_conversation:
            # Update the existing row
            c.execute('''UPDATE Conversations 
                         SET user_messages = ?, assistant_messages = ?
                         WHERE thread_id = ?''',
                      (user_messages_json, assistant_messages_json, thread_id))
        else:
            # Insert a new row
            c.execute('''INSERT INTO Conversations 
                         (thread_id, user_id, username, subject, mode, conversation_name, user_messages, assistant_messages)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (thread_id, user_id, name, self.global_subject, self.global_mode, conversation_name,
                       user_messages_json, assistant_messages_json))

        conn.commit()
        conn.close()

    def retrieve_conversations_by_mode(self, user_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''SELECT mode, conversation_name FROM Conversations WHERE user_id = ?''', (user_id,))
        conversations = c.fetchall()
        conn.close()

        conversations_by_mode = {}
        for mode, conversation_name in conversations:
            if mode not in conversations_by_mode:
                conversations_by_mode[mode] = []
            conversations_by_mode[mode].append(conversation_name)

        return conversations_by_mode

    def retrieve_previous_conversation(self, user_id, conversation_name):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''SELECT * FROM Conversations 
                     WHERE user_id = ? AND conversation_name = ?''', (user_id, conversation_name))
        conversation_data = c.fetchone()
        conn.close()
        if conversation_data:
            conversation = {
                "thread_id": conversation_data[1],  # Assuming thread_id is at index 1
                "user_id": conversation_data[2],  # Assuming user_id is at index 2
                "username": conversation_data[3],  # Assuming username is at index 3
                "subject": conversation_data[4],  # Assuming subject is at index 4
                "mode": conversation_data[5],  # Assuming mode is at index 5
                "conversation_name": conversation_data[6],  # Assuming conversation_name is at index 6
                "user_messages": [],
                "assistant_messages": []
            }
            # Retrieve user and assistant messages
            user_messages_json = conversation_data[7]  # Assuming user_messages is at index 7
            assistant_messages_json = conversation_data[8]  # Assuming assistant_messages is at index 8

            user_messages = json.loads(user_messages_json)
            assistant_messages = json.loads(assistant_messages_json)

            for message_data in user_messages:
                message = {
                    "content": message_data["content"],
                    "timestamp": message_data["timestamp"]
                }
                conversation["user_messages"].append(message)

            for message_data in assistant_messages:
                message = {
                    "content": message_data["content"],
                    "timestamp": message_data["timestamp"]
                }
                conversation["assistant_messages"].append(message)

            return conversation
        else:
            return None

    @staticmethod
    def format_conversation(conversation):
        if not conversation:
            return "Conversation not found."

        formatted_conversation = ""

        user_messages = conversation.get("user_messages", [])
        assistant_messages = conversation.get("assistant_messages", [])
        username = conversation.get('username', 'User')
        subject = conversation.get('subject', 'Subject')
        combined_messages = sorted(user_messages + assistant_messages, key=lambda x: x['timestamp'])

        for message in combined_messages:
            role = username if message in user_messages else f'{subject} Tutee'
            content = message["content"]
            timestamp = message["timestamp"]

            timestamp_str = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

            formatted_conversation += f"({timestamp_str}) {role}: {content}\n\n"
        return formatted_conversation

    def remove_conversation(self, conversation_name):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''DELETE FROM Conversations 
                     WHERE user_id = ? AND conversation_name = ?''', (self.global_user_id, conversation_name))
        conn.commit()
        conn.close()
