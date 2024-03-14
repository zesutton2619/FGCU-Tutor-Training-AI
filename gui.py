import os
import ttkbootstrap as tb
from tkinter import messagebox, simpledialog, filedialog
from backend import Backend
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
import base64


class StartFrame:
    def __init__(self, parent, on_start):
        self.parent = parent
        self.on_start = on_start
        self.key = os.getenv('KEY')
        self.encrypted_password = os.getenv('ENCRYPTED_PASSWORD')

        # Load the background image
        background_image = Image.open('images/login background.png')  # Open the image file
        # Resize the image to fit the parent widget
        resized_image = background_image.resize((parent.winfo_width(), parent.winfo_height()))
        # Convert the resized image to PhotoImage format
        self.background_image = ImageTk.PhotoImage(resized_image)

        # Create frame to hold background image and Start components
        self.frame = tb.Frame(parent)
        self.frame.pack(fill=tb.BOTH, expand=True)

        # Create a label to hold the background image
        self.background_label = tb.Label(self.frame, image=self.background_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create a label for the name of the program text with the same background color
        self.start_label = tb.Label(self.frame, text='FGCU Tutor Training AI', font=('Helvetica', 18),
                                    background='#cdcfcd', foreground='black')
        self.start_label.place(relx=0.5, rely=0.45, anchor=tb.CENTER)

        # Create label for Name
        self.entry_label = tb.Label(self.frame, text='Name:', font=('Helvetica', 18), background='#cbcbcb',
                                    foreground='black')
        self.entry_label.place(relx=0.37, rely=0.5, anchor=tb.CENTER)

        # Create the entry box
        self.entry = tb.Entry(self.frame, width=30, font=('Helvetica', 14))
        self.entry.bind("<Return>", lambda event: self.start())
        self.entry.place(relx=0.5, rely=0.5, anchor=tb.CENTER)

        # Create menu for selecting subjects
        style = tb.Style()
        style.configure('TMenubutton', font=('Helvetica', 14), width=20)
        self.selected_subject = "Select a subject"
        self.subject_menu = tb.Menubutton(self.frame, text=f'{self.selected_subject}', direction="below",
                                          style='primary')
        self.subject_menu.menu = tb.Menu(self.subject_menu, tearoff=False)
        self.subject_menu.configure(menu=self.subject_menu.menu)
        self.subject_menu.menu.config(font=('Helvetica', 14))

        subjects = ["Writing", "Chemistry", "Biology", "Physics", "Nursing", "Math", "Business"]
        for subject in subjects:
            self.subject_menu.menu.add_command(label=subject, command=lambda s=subject: self.set_subject(s))

        self.subject_menu.place(relx=0.5, rely=0.55, anchor=tb.CENTER)

        # # Create menu for selecting mode
        # self.subject_label = tb.Label(self.frame, text='Select the mode for the AI', font=('Helvetica', 14),
        #                               background='#cdcfcd', foreground='black')
        # self.subject_label.place(relx=0.46, rely=0.6, anchor=tb.CENTER)
        self.selected_mode = 'Select AI mode'
        self.mode_menu = tb.Menubutton(self.frame, text=f'{self.selected_mode}', direction="below", style='info')
        self.mode_menu.menu = tb.Menu(self.mode_menu, tearoff=False)
        self.mode_menu.configure(menu=self.mode_menu.menu)
        self.mode_menu.menu.configure(font=('Helvetica', 14))
        modes = ['Tutor', 'Tutee', 'Generate Conversation']
        for mode in modes:
            self.mode_menu.menu.add_command(label=mode, command=lambda m=mode: self.set_mode(m))
        self.mode_menu.place(relx=0.5, rely=0.6, anchor=tb.CENTER)

        # Create the Start button
        style.configure('TButton', font=('Helvetica', 14))
        self.start_button = tb.Button(self.frame, text="Start", command=self.start, width=10, style='success')
        self.start_button.place(relx=0.5, rely=0.65, anchor=tb.CENTER)

    def start(self):
        first_name = self.entry.get()
        if first_name == '':
            messagebox.showerror("Error", "Please enter your first name")
            return
        elif first_name == 'CAA Staff':
            password = simpledialog.askstring("Enter Password", "Please enter your password:", show='*',
                                              parent=self.frame)
            if not self.verify_password(password):
                messagebox.showerror("Error", "Incorrect Password")
                return
        if self.selected_mode not in ['Tutor', 'Tutee', 'Generate Conversation']:
            messagebox.showerror("Error", "Please select mode")
            return
        if self.selected_subject not in ["Writing", "Chemistry", "Biology", "Physics", "Nursing", "Math", "Business"]:
            messagebox.showerror("Error", "Please select subject")
            return
        self.on_start(first_name, self.selected_subject, self.selected_mode)

    def set_subject(self, subject):
        self.selected_subject = subject
        self.subject_menu.config(text=subject)

    def set_mode(self, mode):
        self.selected_mode = mode
        self.mode_menu.config(text=mode)

    def verify_password(self, entered_password):
        # Create a Fernet cipher with the encryption key
        cipher = Fernet(self.key.encode())

        # Decrypt the stored password and decode it
        decrypted_password = cipher.decrypt(base64.b64decode(self.encrypted_password)).decode()

        # Verify if the entered password matches the decrypted password
        return entered_password == decrypted_password


class GUI:
    def __init__(self, root):
        self.conversation_frame = None
        self.input_frame = None
        self.tree_frame = None
        self.tree = None
        self.scrollbar = None
        self.add_message_button = None
        self.exit_button = None
        self.export_button = None
        self.save_button = None
        self.delete_button = None
        self.start_conversation_button = None
        self.info_label = None
        self.conversation_text = None
        self.export_conversation_name = None
        self.export_username = None
        self.export_user_id = None
        self.start_conversation_button_text = None
        self.add_message_button_text = None
        self.message_entry = None
        self.message = None
        self.first_name = None
        self.subject = None
        self.mode = None
        self.path = os.path.join(os.getcwd(), 'Exported Conversations')
        self.root = root
        self.backend = Backend()
        self.previous_conversation_loaded = False
        self.started_conversation = False
        self.root.title("FGCU Training AI")
        self.root.iconbitmap('images/icon.ico')
        self.root.state('zoomed')

        self.main_frame = tb.Frame(self.root)
        self.start_frame = None

        self.show_start_frame()

    def show_start_frame(self):
        if self.main_frame:
            self.main_frame.pack_forget()  # Hide the main frame if it exists
        self.start_frame = StartFrame(self.root, self.on_start)

    def on_start(self, first_name, subject, mode):
        self.first_name = first_name
        self.subject = subject
        self.mode = mode
        self.backend.set_subject(subject)
        self.backend.set_mode(mode)
        print(first_name, subject, mode)
        self.backend.check_username(first_name)
        self.backend.create_conversation_name()  # initialize conversation name
        if self.start_frame:
            self.start_frame.frame.pack_forget()  # Hide the start frame
        self.show_main_frame()

    def show_main_frame(self):
        self.main_frame = tb.Frame(self.root)
        self.main_frame.pack(expand=True, fill=tb.BOTH)

        self.info_label = tb.Label(self.main_frame,
                                   text=f'Name: {self.first_name}, Subject: {self.subject}, 'f'Mode: {self.mode}',
                                   font=('Helvetica', 12))
        self.info_label.pack(side=tb.TOP, fill=tb.X, pady=5, padx=5)

        # Create conversation display area
        self.conversation_frame = tb.Frame(self.main_frame, padding=(10, 10, 0, 10))
        self.conversation_frame.pack(expand=True, fill=tb.BOTH, side=tb.RIGHT)

        # Create conversation display area
        self.conversation_text = tb.Text(self.conversation_frame, wrap=tb.WORD, state='disabled', height=20, width=100,
                                         font=('Helvetica', 12))
        self.conversation_text.pack(expand=True, fill=tb.BOTH, padx=10, pady=5)

        # Add a scrollbar to the conversation text widget
        self.scrollbar = tb.Scrollbar(self.conversation_text, orient=tb.VERTICAL,
                                      command=self.conversation_text.yview, style='primary-round')
        self.scrollbar.pack(side=tb.RIGHT, fill=tb.Y)
        self.conversation_text.config(yscrollcommand=self.scrollbar.set)

        # Create a frame to hold the entry box and button
        self.input_frame = tb.Frame(self.conversation_frame)
        self.input_frame.pack(side=tb.BOTTOM, fill=tb.X, padx=10, pady=10)

        # Add the delete button
        self.delete_button = tb.Button(self.input_frame, text="Delete Conversation", command=self.delete_conversation,
                                       style='warning')
        self.delete_button.grid(row=0, column=5, padx=(5, 10))

        if self.first_name != 'CAA Staff':
            # Add the entry box
            if self.mode != 'Generate Conversation':
                self.message_entry = tb.Text(self.input_frame, wrap=tb.WORD, height=3, width=45, font=('Helvetica', 12))
                self.message_entry.bind("<Return>", lambda event: self.add_message())
                self.message_entry.grid(row=0, column=0, padx=(0, 5))
            # Add the enter button
            if self.mode == 'Generate Conversation':
                self.add_message_button_text = 'Generate New Messages'
            else:
                self.add_message_button_text = 'Enter'
            self.add_message_button = tb.Button(self.input_frame, text=self.add_message_button_text,
                                                command=self.add_message, style='success')
            self.add_message_button.grid(row=0, column=1, padx=(5, 40))

            # Configure column widths to make buttons appear to the right
            self.input_frame.columnconfigure(2, weight=1)  # This will expand empty space between buttons
            self.input_frame.columnconfigure(3, weight=0)  # Adjust the weight to adjust the space between buttons
            self.input_frame.columnconfigure(4, weight=0)  # Adjust the weight to adjust the space between buttons
            self.input_frame.columnconfigure(5, weight=0)  # Adjust the weight to adjust the space between buttons

            # Add the save button
            self.save_button = tb.Button(self.input_frame, text="Save Conversation", command=self.save_conversation)
            self.save_button.grid(row=0, column=4, padx=(5, 5))

            # Add start conversation button
            if self.mode == 'Generate Conversation':
                self.start_conversation_button_text = 'Generate Conversation'
            else:
                self.start_conversation_button_text = 'Start Conversation'
            self.start_conversation_button = tb.Button(self.input_frame, text=self.start_conversation_button_text,
                                                       command=self.start_conversation, style='success')
            self.start_conversation_button.grid(row=0, column=3, padx=(10, 5))

        # Create a frame to hold the TreeView
        self.tree_frame = tb.Frame(self.main_frame, padding=(10, 10, 10, 20))
        self.tree_frame.pack(side=tb.LEFT, fill=tb.BOTH, expand=True)

        # Create the TreeView
        self.tree = tb.Treeview(self.tree_frame, columns=('conversation',), style='primary')
        self.tree.heading('#0', text='Previous Conversations', anchor='w')
        self.tree.column('#0', width=300)
        self.tree.pack(expand=True, fill=tb.BOTH)

        # Create the Exit button
        self.exit_button = tb.Button(self.tree_frame, text="Exit", command=self.exit, style='danger')
        self.exit_button.pack(side=tb.LEFT, anchor='sw', padx=5, pady=10)

        # Create the Export button
        self.export_button = tb.Button(self.tree_frame, text='Export', command=self.export, style='primary')
        self.export_button.pack(side=tb.RIGHT, anchor='se', padx=5, pady=10)

        # Load previous conversations into the TreeView
        self.load_previous_conversations()

        # Bind the tree selection event to load the selected conversation
        self.tree.bind('<<TreeviewSelect>>', self.load_selected_conversation)

    def start_conversation(self):
        if self.previous_conversation_loaded:
            self.clear_conversation()
        else:
            yesno = messagebox.askyesno("Start New Conversation",
                                        "Are you sure you want to start a new conversation?")
            if not yesno:
                return
            else:
                self.clear_conversation()

        self.message = 'Start'
        self.started_conversation = True
        self.add_message()

    def add_message(self):
        if not self.started_conversation and self.previous_conversation_loaded:
            if self.mode == 'Generate Conversation':
                messagebox.showwarning('Error', 'You must generate a conversation first')
            else:
                messagebox.showwarning('Error', 'You must start a conversation first')
            return
        elif self.previous_conversation_loaded:
            self.clear_conversation()
            self.previous_conversation_loaded = False

        self.conversation_text.config(state='normal')  # Set state too normal to allow editing
        conversation_name = self.backend.get_conversation_name()
        user_id = self.backend.get_user_id()

        if self.mode == 'Generate Conversation':
            response = self.backend.generate_response('Continue Conversation', user_id,
                                                      self.first_name, conversation_name)
            self.conversation_text.insert(tb.END, f"{response}\n\n")

        else:

            message = self.message_entry.get("1.0", tb.END)
            if self.message == 'Start':
                response = self.backend.generate_response(self.message, user_id, self.first_name, conversation_name)
                self.conversation_text.insert(tb.END, f"{self.subject} {self.mode}: {response}\n\n")
                self.message = ''
            elif message == '' and self.started_conversation:
                messagebox.showwarning('Error', 'Enter a message')
                return
            else:
                self.conversation_text.insert(tb.END, f"{self.first_name}: {message}\n\n")
                response = self.backend.generate_response(message, user_id, self.first_name, conversation_name)
                self.conversation_text.insert(tb.END, f"{self.subject} {self.mode}: {response}\n\n")

            # Clear the entry box after adding the message
            self.message_entry.delete(1.0, tb.END)

        self.conversation_text.config(state='disabled')

        # Scroll to the bottom of the conversation text widget
        self.conversation_text.see(tb.END)

        return 'break'  # move cursor back to first line

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

    def export(self):
        def on_button_click(export_format):
            # Call the backend function to export the conversation
            if self.export_username is None or self.export_conversation_name is None:
                messagebox.showerror("Error", "Must select previous conversation to export")
                return
            else:
                self.backend.export_conversation(export_format, self.export_conversation_name, self.export_username,
                                                 self.export_user_id, self.path)
            # Close the pop-up window
            top.destroy()

        # Create a new pop-up window
        top = tb.Toplevel()
        top.title("Export Conversation")

        # Set minimum size for the window
        top.minsize(300, 125)

        # Add a label to indicate the purpose of the window
        label = tb.Label(top, text="Select format to export:", font=('Helvetica', 12))
        label.pack(pady=10)

        # Create a frame to hold the buttons horizontally
        button_frame = tb.Frame(top)
        button_frame.pack()

        # Add buttons for exporting to Word Doc and PDF
        word_doc_button = tb.Button(button_frame, text="Word Doc", command=lambda: on_button_click("Word Doc"))
        word_doc_button.pack(side='left', padx=5, pady=5)

        pdf_button = tb.Button(button_frame, text="PDF", command=lambda: on_button_click("PDF"))
        pdf_button.pack(side='left', padx=5, pady=5)

        # Add button to set export directory
        set_directory_button = tb.Button(top, text="Set Export Directory",
                                         command=lambda: self.set_export_directory(selected_directory_label))
        set_directory_button.pack(pady=5)

        # Add label to show directory
        selected_directory_label = tb.Label(top, text=self.path, font=('Helvetica', 12))
        selected_directory_label.pack(side=tb.BOTTOM)

        # Make the pop-up window modal (prevent interaction with other windows)
        top.grab_set()
        # Wait for the pop-up window to be closed before returning
        top.wait_window()

    def set_export_directory(self, label_widget):
        # Open a file dialog to select the export directory
        export_directory = filedialog.askdirectory(initialdir=os.getcwd())

        # Update the label with the selected directory
        if export_directory:
            self.path = export_directory
            label_widget.config(text=self.path)
            print("Export directory selected:", export_directory)
        else:
            print("No export directory selected.")

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
                if self.first_name == 'CAA Staff':
                    parent_item = self.tree.parent(selected_item)
                    username_item = self.tree.parent(parent_item)
                    username_text = self.tree.item(username_item, 'text')
                    username = username_text.split("'s Conversations")[0]
                    user_id = self.backend.get_user_id_by_username(username)
                else:
                    user_id = self.backend.get_user_id()
                self.backend.remove_conversation(conversation_name, user_id)
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

        if self.first_name == 'CAA Staff':
            conversations_by_username = self.backend.retrieve_conversations_by_username(self.first_name)
            for username, data in conversations_by_username.items():
                user_node = self.tree.insert('', 'end', text=f"{username}'s Conversations")
                for mode, conversations in data.items():
                    if mode == 'Generate Conversation':
                        mode_node = self.tree.insert(user_node, 'end', text=f"Generated Conversations")
                    else:
                        mode_node = self.tree.insert(user_node, 'end', text=f"{mode} Conversations")
                    for conversation in conversations:
                        self.tree.insert(mode_node, 'end', text=conversation)
        else:
            # Retrieve previous conversations from the backend grouped by mode
            user_id = self.backend.get_user_id()
            conversations_by_mode = self.backend.retrieve_conversations_by_mode(user_id)

            # Insert mode folders and conversations into the TreeView
            for mode, conversations in conversations_by_mode.items():
                if mode == 'Generate Conversation':
                    mode_item = self.tree.insert('', 'end', text="Generated Conversations")
                else:
                    mode_item = self.tree.insert('', 'end', text=f"{mode} Conversations")
                for conversation in conversations:
                    self.tree.insert(mode_item, 'end', text=conversation)

        self.tree.tag_configure('big_font', font=('Helvetica', 10))
        for item in self.tree.get_children():
            self.tree.item(item, tags=('big_font',))

    def load_selected_conversation(self, event):
        self.previous_conversation_loaded = True
        # Get the selected item from the TreeView
        selected_item = self.tree.selection()
        if not selected_item:  # Check if nothing is selected
            return

        selected_item = selected_item[0]  # Get the first selected item

        # Retrieve the conversation name associated with the selected item
        conversation_name = self.tree.item(selected_item, 'text')

        if self.first_name == 'CAA Staff':
            parent_item = self.tree.parent(selected_item)
            username_item = self.tree.parent(parent_item)
            username_text = self.tree.item(username_item, 'text')
            username = username_text.split("'s Conversations")[0]
            if username not in ['Tutee Conversations', 'Tutor Conversations', 'Generated Conversations', '']:
                user_id = self.backend.get_user_id_by_username(username)
            else:
                return

        else:
            username = self.first_name
            user_id = self.backend.get_user_id()
        print("conversation name", conversation_name)
        # Retrieve the conversation from the backend
        self.export_conversation_name = conversation_name
        self.export_username = username
        self.export_user_id = user_id
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

    def clear_conversation(self):
        # Clear the conversation display area
        self.conversation_text.config(state='normal')  # Set state too normal to allow editing
        self.conversation_text.delete(1.0, tb.END)  # Clear existing conversation
        self.conversation_text.config(state='disabled')  # Set state to disabled to disable editing

    def exit(self):
        self.clear_conversation()
        self.show_start_frame()


def start_gui():
    root = tb.Window(themename='darkly')
    gui = GUI(root)
    root.mainloop()
