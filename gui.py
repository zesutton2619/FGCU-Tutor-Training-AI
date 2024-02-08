import ttkbootstrap as tb
import backend


class GUI:
    def __init__(self, root):
        self.root = root
        self.previous_conversation_loaded = False
        self.root.title("FGCU Training AI")
        self.root.iconbitmap('images/icon.ico')
        self.root.state('zoomed')

        # Create conversation display area
        self.conversation_frame = tb.Frame(self.root, padding=(10, 10, 0, 10))
        self.conversation_frame.pack(expand=True, fill=tb.BOTH, side=tb.RIGHT)

        # Create conversation display area
        self.conversation_text = tb.Text(self.conversation_frame, wrap=tb.WORD, state='disabled', height=20, width=100)
        self.conversation_text.pack(expand=True, fill=tb.BOTH, padx=10, pady=10)

        # Add a scrollbar to the conversation text widget
        self.scrollbar = tb.Scrollbar(self.conversation_text, orient=tb.VERTICAL,
                                      command=self.conversation_text.yview, style='secondary-round')
        self.scrollbar.pack(side=tb.RIGHT, fill=tb.Y)
        self.conversation_text.config(yscrollcommand=self.scrollbar.set)

        # Create a frame to hold the entry box and button
        self.input_frame = tb.Frame(self.conversation_frame)
        self.input_frame.pack(side=tb.BOTTOM, fill=tb.X, padx=10, pady=10)

        # Add the entry box
        self.add_message_entry = tb.Entry(self.input_frame, width=70)
        self.add_message_entry.bind("<Return>", lambda event: self.add_message())
        self.add_message_entry.pack(side=tb.LEFT, padx=(0, 5))

        # Add the enter button
        self.add_message_button = tb.Button(self.input_frame, text="Enter", command=self.add_message)
        self.add_message_button.pack(side=tb.LEFT)

        # Add the save button
        self.save_button = tb.Button(self.input_frame, text="Save", command=self.save_conversation)
        self.save_button.pack(side=tb.RIGHT)

        # Create a frame to hold the TreeView
        self.tree_frame = tb.Frame(self.root, padding=(10, 10, 10, 10))
        self.tree_frame.pack(side=tb.LEFT, fill=tb.BOTH)

        # Create the TreeView
        self.tree = tb.Treeview(self.tree_frame, columns=('conversation',), style='primary')
        self.tree.heading('#0', text='Previous Conversations', anchor='w')
        self.tree.column('#0', stretch=True)
        self.tree.pack(expand=True, fill=tb.BOTH)

        # Load previous conversations into the TreeView
        self.load_previous_conversations()

        # Bind the tree selection event to load the selected conversation
        self.tree.bind('<<TreeviewSelect>>', self.load_selected_conversation)

    def add_message(self):
        if self.previous_conversation_loaded:
            self.clear_conversation()
            self.previous_conversation_loaded = False
        # Get the message from the entry box
        # self.load_previous_conversations()  # load previous conversations again
        message = self.add_message_entry.get()

        # Simulate adding a message to the conversation display
        self.conversation_text.config(state='normal')  # Set state to normal to allow editing
        self.conversation_text.insert(tb.END, f"User: {message}\n")
        # response = "test response"  # Replace with actual response
        conversation_name = backend.get_conversation_name()
        response = backend.generate_response(message, 938, 'Zach', conversation_name)
        self.conversation_text.insert(tb.END, f"Assistant: {response}\n")
        self.conversation_text.config(state='disabled')  # Set state to disabled to disable editing

        # Clear the entry box after adding the message
        self.add_message_entry.delete(0, tb.END)

        # Scroll to the bottom of the conversation text widget
        self.conversation_text.see(tb.END)

    def save_conversation(self):
        # reload previous conversations
        self.load_previous_conversations()

        # Clear the conversation display area
        self.clear_conversation()

        backend.create_conversation_name()  # create new conversation name
        print("new conversation name:  ", backend.get_conversation_name())
        print("Conversation cleared. You can start a new conversation now.")

    def load_previous_conversations(self):
        self.previous_conversation_loaded = True
        # Clear existing items in the TreeView
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Retrieve previous conversations from the backend
        previous_conversations = backend.retrieve_previous_conversation_names(938)

        # Insert previous conversations into the TreeView
        for conversation in previous_conversations:
            self.tree.insert('', 'end', text=conversation)

    def load_selected_conversation(self, event):
        self.previous_conversation_loaded = True
        # Get the selected item from the TreeView
        selected_item = self.tree.selection()
        if not selected_item:  # Check if nothing is selected
            return

        selected_item = selected_item[0]  # Get the first selected item

        # Retrieve the conversation name associated with the selected item
        conversation_name = self.tree.item(selected_item, 'text')

        # Retrieve the user_id (replace '938' with the actual user_id)
        user_id = 938
        print("conversation name", conversation_name)
        # Retrieve the conversation from the backend
        conversation = backend.retrieve_previous_conversation(user_id, conversation_name)
        # print(conversation)
        if conversation:
            # Format the conversation for display
            formatted_conversation = backend.format_conversation(conversation)
            print("formatting done")
            # Display the selected conversation in the conversation text widget
            self.conversation_text.config(state='normal')  # Set state to normal to allow editing
            self.conversation_text.delete(1.0, tb.END)  # Clear existing conversation
            self.conversation_text.insert(tb.END, formatted_conversation)  # Insert selected conversation
            self.conversation_text.config(state='disabled')  # Set state to disabled to disable editing
        else:
            # If conversation is not found, display a message
            self.conversation_text.config(state='normal')  # Set state to normal to allow editing
            self.conversation_text.delete(1.0, tb.END)  # Clear existing conversation
            self.conversation_text.insert(tb.END, "Conversation not found.")  # Insert message
            self.conversation_text.config(state='disabled')  # Set state to disabled to disable editing

    def clear_conversation(self):
        # Clear the conversation display area
        self.conversation_text.config(state='normal')  # Set state to normal to allow editing
        self.conversation_text.delete(1.0, tb.END)  # Clear existing conversation
        self.conversation_text.config(state='disabled')  # Set state to disabled to disable editing


def start_gui():
    root = tb.Window(themename='cyborg')
    gui = GUI(root)
    root.mainloop()

