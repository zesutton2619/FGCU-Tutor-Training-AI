from openai import OpenAI
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi
import time
import os
import random

load_dotenv()
ca = certifi.where()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
print(OPENAI_API_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)

MONGO_URI = os.getenv("MONGO_URI")
client_mongo = MongoClient(MONGO_URI)
db = client_mongo["Test"]  # Replace with your actual database name
threads_collection = db["Threads"]
conversations_collection = db["Conversations"]


# --------------------------------------------------------------
# Thread management
# --------------------------------------------------------------
def check_if_thread_exists(user_wa_id):
    thread = threads_collection.find_one({"wa_id": user_wa_id})
    return thread["thread_id"] if thread else None


def store_thread(user_wa_id, thread_id):
    thread_data = {"wa_id": user_wa_id, "thread_id": thread_id}
    threads_collection.insert_one(thread_data)


# --------------------------------------------------------------
# Generate response
# --------------------------------------------------------------
def generate_response(message_body, user_wa_id, name):
    # Check if there is already a thread_id for the wa_id
    thread_id = check_if_thread_exists(wa_id)

    # If a thread doesn't exist, create one and store it
    if thread_id is None:
        print(f"Creating new thread for {name} with wa_id {user_wa_id}")
        thread = client.beta.threads.create()
        store_thread(user_wa_id, thread.id)
        thread_id = thread.id

    # Otherwise, retrieve the existing thread
    else:
        print(f"Retrieving existing thread for {name} with wa_id {user_wa_id}")
        thread = client.beta.threads.retrieve(thread_id)

    # Add message to thread
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_body,
    )

    # Run the assistant and get the new message
    new_message = run_assistant(thread)

    print(f"To {name}:", new_message)
    return new_message


# --------------------------------------------------------------
# Run assistant
# --------------------------------------------------------------
def run_assistant(thread):
    # Retrieve the Assistant
    assistant = client.beta.assistants.retrieve("asst_cPu94bL3l0kzcPaExKM270Cx")

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    # Wait for completion
    while run.status != "completed":
        # Be nice to the API
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    # Retrieve the Messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    print("messages: ", messages)
    new_message = messages.data[0].content[0].text.value
    print(f"Generated message: {new_message}")
    store_conversation(messages)
    return new_message


# Function to store conversation in the database
def store_conversation(conversation):
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

    # Update existing document or insert new document
    conversation_data = {
        "thread_id": thread_id,
        "user_message": user_messages,
        "assistant_message": assistant_messages
    }

    conversations_collection.replace_one(
        {"thread_id": thread_id},
        conversation_data,
        upsert=True
    )


# --------------------------------------------------------------
# Test assistant
# --------------------------------------------------------------

if __name__ == "__main__":
    print(certifi.where())
    try:
        client_mongo.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    print("FGCU Tutor Trainer Chatbot. Type 'exit' to end.")
    user_name = input("Enter your name: ")
    wa_id = random.randint(100, 999)  # unique identifier for the user
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break

        generate_response(user_input, wa_id, user_name)
