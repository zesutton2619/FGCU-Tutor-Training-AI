from openai import OpenAI
from dotenv import load_dotenv
from pymongo import MongoClient
from docx import Document
from fpdf import FPDF
import time
import os
import datetime
import random

load_dotenv()


class Backend:
    def __init__(self):
        OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=OPENAI_API_KEY)

        MONGO_URI = os.getenv("MONGO_URI")
        self.client_mongo = MongoClient(MONGO_URI)
        self.db = self.client_mongo["Test"]  # Replace with your actual database name
        self.conversations_collection = self.db["Conversations"]  # Conversations collection inside Test database
        self.user_id_collection = self.db["User ID"]  # User ID collection inside Test database
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
        self.generate_conversation_assistant_ids = {
            'Writing': 'asst_WqDmAHC9pa4UV38zYlTPo69x',
            'Chemistry': 'asst_IJwae2Gyx5lIfAHqyok1YseB',
            'Biology': 'asst_rrg0vXS9kakM0ahggvSd4l0z',
            'Physics': 'asst_cXq2JK7cFj6CEixHb9AYiyPV',
            'Nursing': 'asst_4A9ckkItbVIkUV9lECsEUScH',
            'Math': 'asst_VfXLcUHfYqn83qddaLHk0bPx',
            'Business': 'asst_rzDLQwfj6ZZIIB5u0RsuwDIO'
        }

    def generate_user_id(self):
        self.global_user_id = random.randint(100, 999)
        return self.global_user_id

    def create_conversation_name(self):
        # Find the maximum conversation number among existing conversations for the current user
        max_conversation_number = 0
        existing_conversations = self.conversations_collection.find({'user_id': self.global_user_id})
        for conversation in existing_conversations:
            conversation_name = conversation.get("conversation_name")
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
        user_data = self.user_id_collection.find_one({"username": username})

        if user_data:
            self.global_user_id = user_data["user_id"]
            return self.global_user_id
        else:
            self.global_user_id = self.generate_user_id()
            self.user_id_collection.insert_one(
                {
                    "user_id": self.global_user_id,
                    "username": username
                }
            )

    def set_subject(self, subject_name):
        self.global_subject = subject_name

    def set_mode(self, mode):
        self.global_mode = mode

    # --------------------------------------------------------------
    # Thread management
    # --------------------------------------------------------------

    def check_if_thread_exists(self, user_id, conversation_name):
        # filter by user_id and conversation name and look for thread id
        thread = self.conversations_collection.find_one({"user_id": user_id, "conversation_name": conversation_name})
        return thread["thread_id"] if thread else None

    # --------------------------------------------------------------
    # Generate response
    # --------------------------------------------------------------

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

    # --------------------------------------------------------------
    # Run assistant
    # --------------------------------------------------------------

    def run_assistant(self, thread, user_id, name, conversation_name):
        if self.global_mode == 'Tutee':
            assistant_id = self.tutee_assistant_ids[self.global_subject]
        elif self.global_mode == 'Generate Conversation':
            assistant_id = self.generate_conversation_assistant_ids[self.global_subject]
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
        self.store_conversation(messages, user_id, name, conversation_name)
        return new_message

    # --------------------------------------------------------------
    # Function to store conversation in the database
    # --------------------------------------------------------------

    def store_conversation(self, conversation, user_id, name, conversation_name):
        thread_id = conversation.data[0].thread_id

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

        conversation_data = {
            "thread_id": thread_id,
            "user_id": user_id,
            "username": name,
            "subject": self.global_subject,
            "mode": self.global_mode,
            "conversation_name": conversation_name,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages
        }

        self.conversations_collection.replace_one(
            {"thread_id": thread_id},
            conversation_data,
            upsert=True
        )

    # --------------------------------------------------------------
    # Retrieve previous conversation names
    # --------------------------------------------------------------

    def retrieve_previous_conversation_names(self, user_id):
        conversations = self.conversations_collection.find({"user_id": user_id})
        return list(conversations)

    # --------------------------------------------------------------
    # Retrieve previous conversation
    # --------------------------------------------------------------

    def retrieve_previous_conversation(self, user_id, conversation_name):
        conversation = self.conversations_collection.find_one({"user_id": user_id,
                                                               "conversation_name": conversation_name})
        if conversation:
            print("found conversation")
            return conversation
        else:
            return None

    # --------------------------------------------------------------
    # Format conversation for display
    # --------------------------------------------------------------

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
        # print(formatted_conversation)
        return formatted_conversation

    # --------------------------------------------------------------
    # Remove conversation
    # --------------------------------------------------------------

    def remove_conversation(self, conversation_name):
        print("user id", self.global_user_id)
        print("conversation name: ", conversation_name)
        self.conversations_collection.find_one_and_delete({'user_id': self.global_user_id,
                                                           'conversation_name': conversation_name})
# --------------------------------------------------------------
# Export conversation to word document or pdf
# --------------------------------------------------------------


class ConversationExporter:

    def __init__(self, MONGO_URI):
        self.MONGO_URI = MONGO_URI
        self.client_mongo = MongoClient(self.MONGO_URI)
        self.db = self.client_mongo["Test"]
        self.conversations_collection = self.db["Conversations"]

    def export_to_word(self, filename, conversation_data):
        document = Document()

        user_messages = None
        assistant_messages = None
        for document in conversation_data:
            user_messages = document.get('user_messages', [])
            assistant_messages = document.get('assistant_messages', [])

        # Add user and assistant messages to the document
        for message in user_messages:
            document.add_paragraph(f"User: {message['content']}")
        for message in assistant_messages:
            document.add_paragraph(f"Tutor: {message['content']}")

        # Save the document
        document.save(filename)

    def export_to_pdf(self, filename, conversation_data):
        # Initialize PDF object
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Add a page
        pdf.add_page()

        # Set font for the entire document
        pdf.set_font("Times New Roman", size=12)

        # Add content to the PDF
        for message in conversation_data:
            user_messages = message.get('user_messages', [])
            assistant_messages = message.get('assistant_messages', [])

            for user_message in user_messages:
                pdf.cell(0, 10, f"User: {user_message['content']}", ln=True)

            for assistant_message in assistant_messages:
                pdf.cell(0, 10, f"Tutor: {assistant_message['content']}", ln=True)

        # Save the PDF to the specified filename
        pdf.output(filename)

        if __name__ == "__main__":
            # Fetch MongoDB URI from environment variable
            mongo_uri = os.getenv(self.MONGO_URI)

            # Create an instance of ConversationExporter
            exporter = ConversationExporter(self.MONGO_URI)

            # Export conversation to Word document
            exporter.export_to_word("conversation.docx")
