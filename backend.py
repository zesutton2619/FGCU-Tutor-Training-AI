from openai import OpenAI
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi
import time
import os
import datetime
import random
import string

load_dotenv()
ca = certifi.where()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

MONGO_URI = os.getenv("MONGO_URI")
client_mongo = MongoClient(MONGO_URI)
db = client_mongo["Test"]  # Replace with your actual database name
threads_collection = db["Threads"]  # Thread collection inside Test database
conversations_collection = db["Conversations"]  # Conversations collection inside Test database
global_conversation_name = ''
global_user_id = 0


def generate_random_name(length=8):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))


def generate_user_id():
    global global_user_id
    global_user_id = random.randint(100, 999)
    return global_user_id


def get_user_id():
    return global_user_id


def get_conversation_name():
    return global_conversation_name


def create_conversation_name():
    global global_conversation_name
    global_conversation_name = generate_random_name()
    return global_conversation_name


# --------------------------------------------------------------
# Thread management
# --------------------------------------------------------------
def check_if_thread_exists(user_id, conversation_name):
    # filter by user_id and conversation name and look for thread id
    thread = threads_collection.find_one({"user_id": user_id, "conversation_name": conversation_name})
    return thread["thread_id"] if thread else None


def store_thread(user_id, thread_id, conversation_name):
    # Store thread in collection with user_id and conversation_name
    thread_data = {"user_id": user_id, "thread_id": thread_id, "conversation_name": conversation_name}
    threads_collection.insert_one(thread_data)


# --------------------------------------------------------------
# Generate response
# --------------------------------------------------------------
def generate_response(message_body, user_id, name, conversation_name):
    thread_id = check_if_thread_exists(user_id, conversation_name)

    if thread_id is None:
        print(f"Creating new thread for {name} with user_id {user_id}")
        thread = client.beta.threads.create()
        store_thread(user_id, thread.id, conversation_name)
        thread_id = thread.id
    else:
        print(f"Retrieving existing thread for {name} with wa_id {user_id}")
        thread = client.beta.threads.retrieve(thread_id)

    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_body,
    )

    new_message = run_assistant(thread, user_id, name, conversation_name)
    print("Current conversation: ", conversation_name)
    print(f"To {name}:", new_message)
    return new_message


# --------------------------------------------------------------
# Run assistant
# --------------------------------------------------------------
def run_assistant(thread, user_id, name, conversation_name):
    assistant = client.beta.assistants.retrieve("asst_cPu94bL3l0kzcPaExKM270Cx")

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    while run.status != "completed":
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value
    store_conversation(messages, user_id, name, conversation_name)
    return new_message


# --------------------------------------------------------------
# Function to store conversation in the database
# --------------------------------------------------------------
def store_conversation(conversation, user_id, name, conversation_name):
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
        "user_name": name,
        "conversation_name": conversation_name,
        "user_messages": user_messages,
        "assistant_messages": assistant_messages
    }

    conversations_collection.replace_one(
        {"thread_id": thread_id},
        conversation_data,
        upsert=True
    )


# --------------------------------------------------------------
# Retrieve previous conversation names
# --------------------------------------------------------------
def retrieve_previous_conversation_names(user_id):
    conversation_names = conversations_collection.distinct("conversation_name", {"user_id": user_id})
    return conversation_names


# --------------------------------------------------------------
# Retrieve previous conversation
# --------------------------------------------------------------
def retrieve_previous_conversation(user_id, conversation_name):
    conversation = conversations_collection.find_one({"user_id": user_id, "conversation_name": conversation_name})
    if conversation:
        print("found conversation")
        return conversation
    else:
        return None


# --------------------------------------------------------------
# Format conversation for display
# --------------------------------------------------------------
def format_conversation(conversation):
    if not conversation:
        return "Conversation not found."

    formatted_conversation = ""

    user_messages = conversation.get("user_messages", [])
    assistant_messages = conversation.get("assistant_messages", [])
    user_name = conversation.get('user_name', 'User')
    combined_messages = sorted(user_messages + assistant_messages, key=lambda x: x['timestamp'])

    for message in combined_messages:
        role = user_name if message in user_messages else "Assistant"
        content = message["content"]
        timestamp = message["timestamp"]

        timestamp_str = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

        formatted_conversation += f"({timestamp_str}) {role}: {content}\n"
    # print(formatted_conversation)
    return formatted_conversation
