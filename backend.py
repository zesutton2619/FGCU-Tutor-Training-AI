import boto3
from boto3.dynamodb.conditions import Key, Attr
from cryptography.fernet import Fernet
from openai import OpenAI
from dotenv import load_dotenv
from docx import Document
from fpdf import FPDF
import time
import os
import datetime
import random
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

load_dotenv()


class Backend:
    """
        Backend class for managing conversations and database operations.

        Attributes:
            client (OpenAI): OpenAI client for accessing API.
            dynamodb (DynamoDB): AWS DynamoDB.
            global_conversation_name (str): Global conversation name.
            global_user_id (int): Global user ID.
            global_subject (str): Global subject.
            global_mode (str): Global mode.
            tutee_assistant_ids (dict): Dictionary mapping subjects to assistant IDs.
        Functions:
            generate_user_id: Generates user ID
            create_conversation_name: Generates conversation name based on subject and mode
            get_user_id: Gets user ID
            get_user_id_by_username: Gets user ID by querying database for user ID
            get_conversation_name: Gets conversation name
            check_username: Checks if user ID exists in database
            set_subject: Sets the subject
            set_mode: Sets the mode
            check_if_thread_exits: Checks if thread exists in database based on user_id and conversation name
            generate_response: Adds message to assistant thread
            run_assistant: Runs assistant and gets response from API
            store_conversation: Stores Conversation in database
            retrieve_conversations_by_mode: Retrieves conversations by mode from database
            retrieve_conversations_by_username: Retrieves conversations by username from database
            retrieve_previous_conversation: Retrieves previous conversation from database
            remove_conversation: Removes conversation from database
            export_conversation: Exports conversation in PDF or Word Doc
            format_conversation: Formats conversation for display and export
    """

    def __init__(self):
        """
            Initializes the Backend object.
        """
        OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
        os.environ['AWS_PROFILE'] = "Zach-Test"
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.conversations_table = self.dynamodb.Table('Conversations')
        self.user_id_table = self.dynamodb.Table('User_ID')
        self.caa_key = os.environ.get("KEY")
        self.fernet = Fernet(self.caa_key)
        self.diagram_directory = ''
        self.global_conversation_name = ''
        self.global_user_id = 0
        self.global_subject = ''
        self.global_mode = ''
        self.global_username = ''
        self.thread_exists = False
        self.evaluate_conversation = False
        self.generate_conversation_mode = ''
        self.conversations_by_username = {}
        # self.conversations_by_username = \
        #     {
        #         'Zach': {
        #             'Generate Conversation': ['Math Generated Conversation 4', 'Math Generated Conversation 3',
        #                                       'Math Generated Conversation 1', 'Math Generated Conversation 2'],
        #             'Tutee': ['Math Tutee Conversation 4', 'Math Tutee Conversation 3',
        #                       'Math Tutee Conversation 1', 'Math Tutee Conversation 2'],
        #             'Tutor': ['Math Tutor Conversation 1', 'Math Tutor Conversation 2']
        #         },
        #         'Test': {
        #             'Generate Conversation': ['Math Generated Conversation 1'],
        #             'Tutee': ['Math Tutee Conversation 4', 'Math Tutee Conversation 3',
        #                       'Math Tutee Conversation 1', 'Math Tutee Conversation 2'],
        #             'Tutor': ['Math Tutor Conversation 1']
        #         },
        #         'John': {
        #             'Generate Conversation': ['Writing Generated Conversation 1'],
        #             'Tutee': ['Writing Tutee Conversation 4', 'Writing Tutee Conversation 3',
        #                       'Writing Tutee Conversation 1', 'Writing Tutee Conversation 2'],
        #             'Tutor': ['Writing Tutor Conversation 1']
        #         },
        #         'Alice': {
        #             'Generate Conversation': ['Chemistry Generated Conversation 1'],
        #             'Tutee': ['Chemistry Tutee Conversation 4', 'Chemistry Tutee Conversation 3',
        #                       'Chemistry Tutee Conversation 1', 'Chemistry Tutee Conversation 2'],
        #             'Tutor': ['Chemistry Tutor Conversation 1']
        #         },
        #         'Bob': {
        #             'Generate Conversation': ['Biology Generated Conversation 1'],
        #             'Tutee': ['Biology Tutee Conversation 4', 'Biology Tutee Conversation 3',
        #                       'Biology Tutee Conversation 1', 'Biology Tutee Conversation 2'],
        #             'Tutor': ['Biology Tutor Conversation 1']
        #         },
        #         'Emma': {
        #             'Generate Conversation': ['Physics Generated Conversation 1'],
        #             'Tutee': ['Physics Tutee Conversation 4', 'Physics Tutee Conversation 3',
        #                       'Physics Tutee Conversation 1', 'Physics Tutee Conversation 2'],
        #             'Tutor': ['Physics Tutor Conversation 1']
        #         },
        #         'David': {
        #             'Generate Conversation': ['Nursing Generated Conversation 1'],
        #             'Tutee': ['Nursing Tutee Conversation 4', 'Nursing Tutee Conversation 3',
        #                       'Nursing Tutee Conversation 1', 'Nursing Tutee Conversation 2'],
        #             'Tutor': ['Nursing Tutor Conversation 1']
        #         },
        #         'Sophia': {
        #             'Generate Conversation': ['Business Generated Conversation 1'],
        #             'Tutee': ['Business Tutee Conversation 4', 'Business Tutee Conversation 3',
        #                       'Business Tutee Conversation 1', 'Business Tutee Conversation 2'],
        #             'Tutor': ['Business Tutor Conversation 1']
        #         },
        #         'Michael': {
        #             'Generate Conversation': ['Math Generated Conversation 5', 'Math Generated Conversation 6',
        #                                       'Math Generated Conversation 7', 'Math Generated Conversation 8'],
        #             'Tutee': ['Math Tutee Conversation 5', 'Math Tutee Conversation 6',
        #                       'Math Tutee Conversation 7', 'Math Tutee Conversation 8'],
        #             'Tutor': ['Math Tutor Conversation 2']
        #         },
        #         'Sarah': {
        #             'Generate Conversation': ['Chemistry Generated Conversation 2'],
        #             'Tutee': ['Chemistry Tutee Conversation 5', 'Chemistry Tutee Conversation 6',
        #                       'Chemistry Tutee Conversation 7', 'Chemistry Tutee Conversation 8'],
        #             'Tutor': ['Chemistry Tutor Conversation 2']
        #         }
        #     }

        self.tutee_assistant_ids = {
            'Writing': 'asst_xqPTYqajw69DTFS2yidhYVBJ',
            'Chemistry': 'asst_M2fmEombFqQpmZHUmUBgkfVJ',
            'Biology': 'asst_A3KVHx9Rp7oM8l585JUAEbIU',
            'Physics': 'asst_2cDZXQUhhR9nvH93rx5dhTG8',
            'Nursing': 'asst_SCNZeLiWbJ1XmkLM9GTINtPV',
            'Math': 'asst_cPu94bL3l0kzcPaExKM270Cx',
            'Business': 'asst_ySOkMWNC06ql3weCpYQN1Pdi'
        }
        self.generate_conversation_ids = {
            'Writing': 'asst_WqDmAHC9pa4UV38zYlTPo69x',
            'Chemistry': 'asst_IJwae2Gyx5lIfAHqyok1YseB',
            'Biology': 'asst_rrg0vXS9kakM0ahggvSd4l0z',
            'Physics': 'asst_cXq2JK7cFj6CEixHb9AYiyPV',
            'Nursing': 'asst_4A9ckkItbVIkUV9lECsEUScH',
            'Math': 'asst_VfXLcUHfYqn83qddaLHk0bPx',
            'Business': 'asst_rzDLQwfj6ZZIIB5u0RsuwDIO'
        }

    def generate_user_id(self):
        """
            Generates a random user ID.

            Returns:
                int: Random user ID.
        """
        self.global_user_id = random.randint(100, 999)
        return self.global_user_id

    def create_conversation_name(self):
        """
            Creates a new conversation name based on subject and mode.

            Returns:
                str: New conversation name.
        """
        # Find the maximum conversation number among existing conversations for the current user
        max_conversation_number = 0
        fe = Key('user_id').eq(self.global_user_id) & (
                Key('conversation_name').begins_with(f"{self.global_subject} {self.global_mode} Conversation ") |
                (Key('conversation_name').begins_with(f"{self.global_subject} Generated Conversation ") & Attr(
                    'mode').eq('Generate Conversation'))
        )
        response = self.conversations_table.scan(FilterExpression=fe, ProjectionExpression='conversation_name')

        for item in response['Items']:
            conversation_name = item['conversation_name']
            if (conversation_name and
                    (conversation_name.startswith(f"{self.global_subject} {self.global_mode} Conversation ") or
                     (conversation_name.startswith(f"{self.global_subject} Generated Conversation "))
                     and self.global_mode == 'Generate Conversation')):
                conversation_number = int(conversation_name.split(" ")[-1])
                max_conversation_number = max(max_conversation_number, conversation_number)

        # Increment the maximum conversation number to generate the next conversation name
        new_conversation_number = max_conversation_number + 1
        if self.global_mode == "Generate Conversation":
            self.global_conversation_name = (f"{self.global_subject} Generated Conversation "
                                             f"{new_conversation_number}")

        else:
            self.global_conversation_name = (f"{self.global_subject} {self.global_mode} "
                                             f"Conversation {new_conversation_number}")
        print("new generated conversation name: ", self.global_conversation_name)
        return self.global_conversation_name

    def get_user_id(self):
        """
            Retrieves the global user ID.

            Returns:
                int: Global user ID.
        """
        return self.global_user_id

    def get_user_id_by_username(self, username):
        """
        Retrieves the user ID based on the provided username.

        Args:
            username (str): Username of the user.

        Returns:
            int: User ID associated with the username.

        """
        print("username:", username)
        response = self.user_id_table.scan(FilterExpression=Attr('username').eq(username))
        items = response.get('Items', [])
        if items:
            # Assuming username is unique, so only one item should be returned
            item = items[0]
            return item['user_id']
        else:
            return None

    def get_conversation_name(self):
        """
            Retrieves the global conversation name.

            Returns:
                str: Global conversation name.
        """
        return self.global_conversation_name

    def check_username(self, username):
        """
            Checks if a username exists in the database and returns the corresponding user ID.
            If not, generates a new user ID and inserts the username into the database.

            Args:
                username (str): Username to check.

            Returns:
                int: User ID.
        """
        response = self.user_id_table.scan(FilterExpression=Attr('username').eq(username))
        if response['Items']:
            self.global_user_id = response['Items'][0]['user_id']
            return self.global_user_id
        else:
            # User not found, generate a new user ID and insert the username
            self.global_user_id = self.generate_user_id()
            self.user_id_table.put_item(Item={'user_id': self.global_user_id, 'username': username})
            return self.global_user_id

    def set_subject(self, subject_name):
        """
            Sets the global subject.

            Args:
                subject_name (str): Subject name.
        """
        self.global_subject = subject_name

    def set_mode(self, mode):
        """
            Sets the global mode.

            Args:
                mode (str): Mode ('Tutee', 'Tutor', 'Generate Conversation').
        """
        self.global_mode = mode

    def set_username(self, username):
        self.global_username = username

    def set_evaluate_conversation(self, evaluate):
        self.evaluate_conversation = evaluate

    def check_if_thread_exists(self, user_id, conversation_name):
        """
        Checks if a thread with the given user ID and conversation name exists in the database.

        Args:
            user_id (int): User ID.
            conversation_name (str): Conversation name.

        Returns:
            str or None: Thread ID if exists, None otherwise.
        """
        fe = "user_id = :user_id AND conversation_name = :conversation_name"
        eav = {":user_id": user_id, ":conversation_name": conversation_name}

        response = self.conversations_table.scan(FilterExpression=fe, ExpressionAttributeValues=eav)
        if 'Items' in response and len(response['Items']) > 0:
            self.thread_exists = True
            return response['Items'][0]['thread_id']  # Accessing the first item's 'thread_id'
        else:
            self.thread_exists = False
            return None

    def generate_response(self, message_body, user_id, name, conversation_name):
        """
            Generates a response using the OpenAI assistant and stores the conversation in the database.

            Args:
                message_body (str): Message body.
                user_id (int): User ID.
                name (str): Username.
                conversation_name (str): Conversation name.

            Returns:
                str: New message generated by the assistant.
        """
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
        """
            Runs the OpenAI assistant and retrieves messages for a given thread.

            Args:
                thread (Thread): Thread object.
                user_id (int): User ID.
                name (str): Username.
                conversation_name (str): Conversation name.

            Returns:
                str: New message generated by the assistant.
        """
        if self.evaluate_conversation:
            assistant_id = 'asst_siJtmiaoyNlExZQ8V8OXEQG5'
        elif self.global_mode == 'Generate Conversation':
            assistant_id = self.generate_conversation_ids[self.global_subject]
        elif self.global_mode == 'Tutee':
            assistant_id = self.tutee_assistant_ids[self.global_subject]
        elif self.global_mode == 'Tutor':
            assistant_id = 'asst_IPJi4k5UXGPNkHZ5nTSjnZ5S'
        else:
            assistant_id = 'asst_IPJi4k5UXGPNkHZ5nTSjnZ5S'
        print("Generate Conversation Mode:", self.generate_conversation_mode, "Assistant:", assistant_id)
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
        """
            Stores the conversation in the database.

            Args:
                thread (Thread): Thread object.
                conversation (Conversation): Conversation object.
                user_id (int): User ID.
                name (str): Username.
                conversation_name (str): Conversation name.
        """
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

        item = {
            'thread_id': thread_id,
            'user_id': user_id,
            'username': name,
            'subject': self.global_subject,
            'mode': self.global_mode,
            'conversation_name': conversation_name,
            'user_messages': user_messages,
            'assistant_messages': assistant_messages
        }

        self.conversations_table.put_item(Item=item)

    def retrieve_conversations_by_mode(self, user_id):
        """
        Retrieves conversations for a user grouped by mode.

        Args:
            user_id (int): User ID.

        Returns:
            dict: Dictionary of conversations grouped by mode.
        """
        conversations_by_mode = {}
        response = self.conversations_table.scan(FilterExpression=Attr('user_id').eq(user_id))
        for item in response['Items']:
            mode = item['mode']
            conversation_name = item['conversation_name']
            if mode not in conversations_by_mode:
                conversations_by_mode[mode] = []
            conversations_by_mode[mode].append(conversation_name)

        print("Conversations by mode: ", conversations_by_mode)

        return conversations_by_mode

    def retrieve_conversations_by_username(self, username):
        """
        Retrieves conversations for users other than the specified username, grouped by username and mode.

        Args:
            username (str): Username of the user to exclude.

        Returns:
            dict: Dictionary of conversations grouped by username and mode.
        """
        fe = "username <> :username"
        response = self.conversations_table.scan(FilterExpression=fe, ExpressionAttributeValues={":username": username})

        self.conversations_by_username = {}
        for item in response['Items']:
            username = item['username']
            mode = item['mode']
            conversation_name = item['conversation_name']

            if username not in self.conversations_by_username:
                self.conversations_by_username[username] = {}
            if mode not in self.conversations_by_username[username]:
                self.conversations_by_username[username][mode] = []
            self.conversations_by_username[username][mode].append(conversation_name)

        print("Conversations by username: ", self.conversations_by_username)
        return self.conversations_by_username

    def retrieve_previous_conversation(self, user_id, conversation_name):
        """
            Retrieves a previous conversation by user ID and conversation name.

            Args:
                user_id (int): User ID.
                conversation_name (str): Conversation name.

            Returns:
                dict or None: Previous conversation data.
        """
        fe = "user_id = :user_id AND conversation_name = :conversation_name"
        eav = {":user_id": user_id, ":conversation_name": conversation_name}

        response = self.conversations_table.scan(FilterExpression=fe, ExpressionAttributeValues=eav)
        print("response: ", response)

        if 'Items' in response and len(response['Items']) > 0:
            # Assuming there's only one matching item
            return response['Items'][0]
        else:
            return None

    def remove_conversation(self, conversation_name, user_id):
        """
            Removes a conversation from the database.

            Args:
                conversation_name (str): Conversation name.
                user_id (int): User ID.
        """
        # Scan for items with the specified user_id
        response = self.conversations_table.scan(FilterExpression=Attr('user_id').eq(user_id))

        # Check if there are any items with the specified user_id
        if 'Items' in response:
            items = response['Items']
            for item in items:
                # Check if the conversation_name matches
                if item['conversation_name'] == conversation_name:
                    # Delete the item using its thread_id (assuming it's available in the item)
                    self.conversations_table.delete_item(Key={'thread_id': item['thread_id']})

    def export_conversation(self, format_of_export, conversation_name, username, user_id, path):
        print("username:", username)
        print("conversation name:", conversation_name)
        conversation = self.retrieve_previous_conversation(user_id, conversation_name)
        formatted_conversation = self.format_conversation(conversation)
        if format_of_export == 'Word Doc':
            doc = Document()
            doc.add_paragraph(formatted_conversation)
            doc.save(os.path.join(path, f"{username} - {conversation_name}.docx"))
        elif format_of_export == 'PDF':
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, formatted_conversation)
            pdf.output(os.path.join(path, f"{username} - {conversation_name}.pdf"))
        return

    def encrypt_data(self, data):
        return self.fernet.encrypt(data)

    def decrypt_data(self, encrypted_data):
        try:
            print("Attempting to decrypt data...")
            decrypted_data = self.fernet.decrypt(encrypted_data)
            print("Data decrypted successfully.")
            return decrypted_data
        except Exception as e:
            print("Error decrypting data:", str(e))
            return None

    def make_total_conversations_per_mode(self):
        modes = ["Generate Conversation", "Tutor", "Tutee"]
        mode_counts = {mode: 0 for mode in modes}
        usernames = list(self.conversations_by_username.keys())

        for username in usernames:
            for mode in modes:
                if mode in self.conversations_by_username[username]:
                    mode_counts[mode] += len(self.conversations_by_username[username][mode])

        self.create_bar_plot(mode_counts, "Total Number of Conversations per Mode", "Mode", "Number of Conversations")
        self.save_encrypted_plot("Total Number of Conversations per Mode")
        plt.show()

    def make_total_conversations_by_mode_per_tutor(self, mode):
        mode_counts = {tutor: 0 for tutor in self.conversations_by_username}
        for tutor, conversations in self.conversations_by_username.items():
            if mode in conversations:
                mode_counts[tutor] = len(conversations[mode])

        self.create_bar_plot(mode_counts, f"Total Number of {mode} Conversations per Tutor", "Tutor",
                             "Total Conversations")
        self.save_encrypted_plot(f"Total Number of {mode} Conversations per Tutor")
        plt.show()

    def make_total_conversations_by_tutor(self, user):
        if user not in self.conversations_by_username:
            print(f"Error: User '{user}' not found in the conversations data.")
            return

        user_data = self.conversations_by_username[user]
        modes = list(user_data.keys())
        mode_counts = {mode: len(user_data[mode]) for mode in modes}

        self.create_bar_plot(mode_counts, f"Total Number of Conversations by Tutor {user}", "Mode",
                             "Number of Conversations")
        self.save_encrypted_plot(f"Total Number of Conversations by Tutor {user}")
        plt.show()

    def save_encrypted_plot(self, title):
        diagram_directory = os.path.join(os.getcwd(), f"{self.global_username} Diagrams")
        if not os.path.exists(diagram_directory):
            os.makedirs(diagram_directory)

        plot_filename = os.path.join(diagram_directory, f"{title.replace(' ', '_').lower()}_plot.png")
        plt.savefig(plot_filename)

        with open(plot_filename, 'rb') as file:
            image_data = file.read()
        encrypted_image_data = self.encrypt_data(image_data)  # Assuming encrypt_data method exists

        encrypted_plot_filename = os.path.join(diagram_directory, f"{title.replace(' ', '_').lower()}_plot.enc")
        with open(encrypted_plot_filename, 'wb') as file:
            file.write(encrypted_image_data)

        os.remove(plot_filename)

    @staticmethod
    def create_bar_plot(data, title, x_label, y_label):
        plt.figure(figsize=(9, 6))
        plt.bar(list(data.keys()), list(data.values()), color='#004785')
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.xticks(rotation=45, ha='right')
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.tight_layout()

    @staticmethod
    def format_conversation(conversation):
        """
        Formats a conversation for display.

        Args:
            conversation (dict): Conversation data.

        Returns:
            str: Formatted conversation.
        """
        if not conversation:
            return "Conversation not found."

        formatted_conversation = ""

        user_messages = conversation.get("user_messages", [])
        assistant_messages = conversation.get("assistant_messages", [])
        username = conversation.get('username', 'User')
        subject = conversation.get('subject', 'Subject')
        mode = conversation.get('mode', 'Mode')
        print("mode in formatted conversation:", mode)
        if mode != 'Generate Conversation':

            combined_messages = sorted(user_messages + assistant_messages, key=lambda x: x['timestamp'])

            for message in combined_messages:
                role = username if message in user_messages else f'{subject} Tutee'

                content = message["content"]
                timestamp = message["timestamp"]

                timestamp_str = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

                formatted_conversation += f"({timestamp_str}) {role}: {content}\n\n"
            return formatted_conversation

        else:
            timestamp = assistant_messages[0]["timestamp"]
            timestamp_str = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            formatted_conversation += f"({timestamp_str})\n"
            for message in assistant_messages:
                content = message["content"]
                formatted_conversation += f"{content}\n"
            return formatted_conversation
