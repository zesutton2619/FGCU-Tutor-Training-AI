import ttkbootstrap as tb
from tkinter import messagebox
from backend import Backend
from PIL import Image, ImageTk


class LoginFrame:
    def __init__(self, parent, on_login):
        self.parent = parent
        self.on_login = on_login

        # Load the background image
        background_image = Image.open('images/login background.png')  # Open the image file
        # Resize the image to fit the parent widget
        resized_image = background_image.resize((parent.winfo_width(), parent.winfo_height()))
        # Convert the resized image to PhotoImage format
        self.background_image = ImageTk.PhotoImage(resized_image)

        # Create frame to hold background image and login components
        self.frame = tb.Frame(parent)
        self.frame.pack(fill=tb.BOTH, expand=True)

        # Create a label to hold the background image
        self.background_label = tb.Label(self.frame, image=self.background_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create a label for the "Login" text with no background
        login_label = tb.Label(self.frame, text='Login', font=('Arial', 18), background='#cdcfcd', foreground='black')
        login_label.place(relx=0.5, rely=0.45, anchor=tb.CENTER)

        # Create the entry box
        self.entry = tb.Entry(self.frame, width=30, font=('Arial', 14))
        self.entry.bind("<Return>", lambda event: self.login())
        self.entry.place(relx=0.5, rely=0.5, anchor=tb.CENTER)

        # Create the login button
        self.login_button = tb.Button(self.frame, text="Login", command=self.login, width=10)
        self.login_button.place(relx=0.5, rely=0.55, anchor=tb.CENTER)

    def login(self):
        first_name = self.entry.get()
        if first_name == '':
            login_label = tb.Label(self.frame, text='Please enter your First Name', font=('Arial', 18),
                                   background='#cdcfcd', foreground='black')
            login_label.place(relx=0.5, rely=0.60, anchor=tb.CENTER)
            return
        self.on_login(first_name)


class GUI:
    def __init__(self, root):
        self.conversation_frame = None
        self.input_frame = None
        self.tree_frame = None
        self.tree = None
        self.scrollbar = None
        self.add_message_button = None
        self.logout_button = None
        self.save_button = None
        self.delete_button = None
        self.start_conversation_button = None
        self.conversation_text = None
        self.add_message_entry = None
        self.message = None
        self.first_name = None
        self.root = root
        self.backend = Backend()
        self.previous_conversation_loaded = False
        self.started_conversation = False
        self.root.title("FGCU Training AI")
        self.root.iconbitmap('images/icon.ico')
        self.root.state('zoomed')

        self.main_frame = tb.Frame(self.root)
        self.login_frame = None

        self.show_login_frame()

    def show_login_frame(self):
        if self.main_frame:
            self.main_frame.pack_forget()  # Hide the main frame if it exists
        self.login_frame = LoginFrame(self.root, self.on_login)

    def on_login(self, first_name):
        self.first_name = first_name
        self.backend.check_username(first_name)
        self.backend.create_conversation_name()  # initialize conversation name
        # self.message = 'Start'
        # self.add_message()
        if self.login_frame:
            self.login_frame.frame.pack_forget()  # Hide the login frame
        self.show_main_frame()

    def show_main_frame(self):
        self.main_frame = tb.Frame(self.root)
        self.main_frame.pack(expand=True, fill=tb.BOTH)

        # Create conversation display area
        self.conversation_frame = tb.Frame(self.main_frame, padding=(10, 10, 0, 10))
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
        self.add_message_button = tb.Button(self.input_frame, text="Enter", command=self.add_message, style='success')
        self.add_message_button.pack(side=tb.LEFT)

        # Add the save button
        self.save_button = tb.Button(self.input_frame, text="Save Conversation", command=self.save_conversation)
        self.save_button.pack(side=tb.RIGHT)

        # Add the delete button
        self.delete_button = tb.Button(self.input_frame, text="Delete Conversation", command=self.delete_conversation,
                                       style='warning')
        self.delete_button.pack(side=tb.RIGHT, padx=10)

        # Add start conversation button
        self.start_conversation_button = tb.Button(self.input_frame, text="Start Conversation",
                                                   command=self.start_conversation, style='success')
        self.start_conversation_button.pack(side=tb.RIGHT, padx=10)

        # Create a frame to hold the TreeView
        self.tree_frame = tb.Frame(self.main_frame, padding=(10, 10, 10, 20))
        self.tree_frame.pack(side=tb.LEFT, fill=tb.BOTH)

        self.logout_button = tb.Button(self.tree_frame, text="Logout", command=self.logout, style='danger')
        self.logout_button.pack(side=tb.BOTTOM, pady=10, anchor='sw')

        # Create the TreeView
        self.tree = tb.Treeview(self.tree_frame, columns=('conversation',), style='primary')
        self.tree.heading('#0', text='Previous Conversations', anchor='w')
        self.tree.column('#0', stretch=True)
        self.tree.pack(expand=True, fill=tb.BOTH)

        # Load previous conversations into the TreeView
        self.load_previous_conversations()

        # Bind the tree selection event to load the selected conversation
        self.tree.bind('<<TreeviewSelect>>', self.load_selected_conversation)

    def start_conversation(self):
        if self.previous_conversation_loaded:
            self.clear_conversation()

        self.message = 'Start'
        self.started_conversation = True
        self.add_message()

    def add_message(self):
        if not self.started_conversation and self.previous_conversation_loaded:
            messagebox.showwarning('Error', 'You must start a conversation first')
            return
        elif self.previous_conversation_loaded:
            self.clear_conversation()
            self.previous_conversation_loaded = False

        self.conversation_text.config(state='normal')  # Set state too normal to allow editing
        message = self.add_message_entry.get()
        if self.message == 'Start':
            conversation_name = self.backend.get_conversation_name()
            user_id = self.backend.get_user_id()
            response = self.backend.generate_response(self.message, user_id, self.first_name, conversation_name)
            self.conversation_text.insert(tb.END, f"Assistant: {response}\n")
            self.message = ''
        elif message == '' and self.started_conversation:
            messagebox.showwarning('Error', 'Enter a message')
            return
        else:
            message = self.add_message_entry.get()
            self.conversation_text.insert(tb.END, f"{self.first_name}: {message}\n")
            conversation_name = self.backend.get_conversation_name()
            user_id = self.backend.get_user_id()
            response = self.backend.generate_response(message, user_id, self.first_name, conversation_name)
            self.conversation_text.insert(tb.END, f"Assistant: {response}\n")

        self.conversation_text.config(state='disabled')

        # Clear the entry box after adding the message
        self.add_message_entry.delete(0, tb.END)

        # Scroll to the bottom of the conversation text widget
        self.conversation_text.see(tb.END)

    def save_conversation(self):
        self.started_conversation = False
        if self.is_conversation_empty():
            messagebox.showwarning('Error', 'Cannot save empty conversation')
            return
        elif self.previous_conversation_loaded:
            messagebox.showwarning('Error', 'Cannot save previously loaded conversation')
            return

        # reload previous conversations
        self.load_previous_conversations()

        # Clear the conversation display area
        self.clear_conversation()

        self.backend.create_conversation_name()  # create new conversation name
        print("new conversation name:  ", self.backend.get_conversation_name())
        print("Conversation cleared. You can start a new conversation now.")

    def is_conversation_empty(self):
        # Get the content of the conversation text widget
        conversation_content = self.conversation_text.get("1.0", tb.END).strip()
        # Check if the content is empty
        return not conversation_content

    def delete_conversation(self):
        if not self.is_conversation_empty():
            # Get the selected conversation
            selected_item = self.tree.selection()
            conversation_name = self.tree.item(selected_item, 'text')

            # Prompt the user for confirmation
            confirmed = messagebox.askyesno("Confirmation",
                                            f"Are you sure you want to delete the conversation '{conversation_name}'?")

            if confirmed:
                # If user confirms deletion, proceed with deletion
                self.backend.remove_conversation(conversation_name)
                self.load_previous_conversations()
                self.clear_conversation()
                print("Deleting conversation")
        else:
            messagebox.showwarning('Error', 'Cannot delete empty conversation')

    def load_previous_conversations(self):
        self.started_conversation = False
        self.previous_conversation_loaded = True
        # Clear existing items in the TreeView
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Retrieve previous conversations from the backend
        user_id = self.backend.get_user_id()
        previous_conversations = self.backend.retrieve_previous_conversation_names(user_id)

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

        user_id = self.backend.get_user_id()
        print("conversation name", conversation_name)
        # Retrieve the conversation from the backend
        conversation = self.backend.retrieve_previous_conversation(user_id, conversation_name)
        # print(conversation)
        if conversation:
            # Format the conversation for display
            formatted_conversation = self.backend.format_conversation(conversation)
            print("formatting done")
            # Display the selected conversation in the conversation text widget
            self.conversation_text.config(state='normal')  # Set state too normal to allow editing
            self.conversation_text.delete(1.0, tb.END)  # Clear existing conversation
            self.conversation_text.insert(tb.END, formatted_conversation)  # Insert selected conversation
            self.conversation_text.config(state='disabled')  # Set state to disabled to disable editing
        else:
            # If conversation is not found, display a message
            self.conversation_text.config(state='normal')  # Set state too normal to allow editing
            self.conversation_text.delete(1.0, tb.END)  # Clear existing conversation
            self.conversation_text.insert(tb.END, "Conversation not found.")  # Insert message
            self.conversation_text.config(state='disabled')  # Set state to disabled to disable editing

    def clear_conversation(self):
        # Clear the conversation display area
        self.conversation_text.config(state='normal')  # Set state too normal to allow editing
        self.conversation_text.delete(1.0, tb.END)  # Clear existing conversation
        self.conversation_text.config(state='disabled')  # Set state to disabled to disable editing

    def logout(self):
        self.clear_conversation()
        self.show_login_frame()


def start_gui():
    root = tb.Window(themename='darkly')
    gui = GUI(root)
    root.mainloop()
