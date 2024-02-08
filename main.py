import backend
import gui


# Test assistant
if __name__ == "__main__":
    backend.create_conversation_name()
    gui.start_gui()
    # try:
    #     backend.client_mongo.admin.command('ping')
    #     print("Pinged your deployment. You successfully connected to MongoDB!")
    # except Exception as e:
    #     print(e)
    # print("FGCU Tutor Trainer Chatbot. Type 'exit' to end.")
    # user_name = input("Enter your name: ")
    # wa_id = random.randint(100, 999)  # unique identifier for the user
    # conversation_name = backend.create_conversation_name()  # Generate a random conversation name
    # print("Conversation name: ", conversation_name)
    # while True:
    #     user_input = input(f"{user_name}: ")
    #     if user_input.lower() == 'exit':
    #         break
    #
    #     backend.generate_response(user_input, 938, 'Zach', conversation_name)
