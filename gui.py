import os
import ttkbootstrap as tb
from tkinter import messagebox, simpledialog, filedialog
from backend import Backend
from data_analysis_menu import DataAnalysisMenu
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
import base64
import re


class StartFrame:
    """ Class representing the initial GUI frame for user input. """

    def __init__(self, parent, on_start):
        """
        Initialize the StartFrame object.

        Args:
            parent: The parent widget.
            on_start: Callback function to be called when the start button is clicked.
        """
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
        self.start_label = tb.Label(self.frame, text='FGCU TutorTech', font=('Helvetica', 18),
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
        self.mode_menu = tb.Menubutton(self.frame, text=f'{self.selected_mode}', direction="below", style='secondary')
        self.mode_menu.menu = tb.Menu(self.mode_menu, tearoff=False)
        self.mode_menu.configure(menu=self.mode_menu.menu)
        self.mode_menu.menu.configure(font=('Helvetica', 14))
        modes = ['Tutor', 'Tutee', 'Generate Conversation']
        for mode in modes:
            self.mode_menu.menu.add_command(label=mode, command=lambda m=mode: self.set_mode(m))
        self.mode_menu.place(relx=0.5, rely=0.6, anchor=tb.CENTER)

        # Create the Start button
        style.configure('TButton', font=('Helvetica', 14))
        self.start_button = tb.Button(self.frame, text="Start", command=self.start, width=10, style='primary')
        self.start_button.place(relx=0.5, rely=0.65, anchor=tb.CENTER)

    def start(self):
        """Handle the start button click event."""
        first_name = self.entry.get()
        if first_name == 'CAA Staff':
            password = simpledialog.askstring("Enter Password", "Please enter your password:", show='*',
                                              parent=self.frame)
            if not self.verify_password(password):
                messagebox.showerror("Error", "Incorrect Password")
                return
        elif first_name == '':
            messagebox.showerror("Error", "Please enter your first name")
            return
        if self.selected_mode not in ['Tutor', 'Tutee', 'Generate Conversation'] and first_name != 'CAA Staff':
            messagebox.showerror("Error", "Please select mode")
            return
        if (self.selected_subject not in ["Writing", "Chemistry", "Biology", "Physics", "Nursing", "Math", "Business"]
                and first_name != 'CAA Staff'):
            messagebox.showerror("Error", "Please select subject")
            return
        self.on_start(first_name, self.selected_subject, self.selected_mode)

    def set_subject(self, subject):
        """
        Set the selected subject.

        Args:
            subject: The selected subject.
        """
        self.selected_subject = subject
        self.subject_menu.config(text=subject)

    def set_mode(self, mode):
        """
        Set the selected mode.

        Args:
            mode: The selected mode.
        """
        self.selected_mode = mode
        self.mode_menu.config(text=mode)

    def verify_password(self, entered_password):
        """
        Verify the entered password.

        Args:
            entered_password: The password entered by the user.

        Returns:
            bool: True if the entered password matches the decrypted password, False otherwise.
        """
        # Create a Fernet cipher with the encryption key
        cipher = Fernet(self.key.encode())

        # Decrypt the stored password and decode it
        decrypted_password = cipher.decrypt(base64.b64decode(self.encrypted_password)).decode()

        # Verify if the entered password matches the decrypted password
        return entered_password == decrypted_password


class GUI:
    """Class representing the main GUI."""

    def __init__(self, root):
        """
        Initialize the GUI object.

        Args:
            root: The root window.
        """
        self.info_frame = None
        self.conversation_frame_inner = None
        self.conversation_frame = None
        self.input_frame = None
        self.tree_frame = None
        self.exit_and_export_frame = None
        self.mode_menu = None
        self.subject_menu = None
        self.tree = None
        self.scrollbar = None
        self.add_message_button = None
        self.exit_button = None
        self.export_button = None
        self.save_button = None
        self.delete_button = None
        self.start_conversation_button = None
        self.view_data_analysis_button = None
        self.evaluate_button = None
        self.info_label = None
        self.conversation_text = None
        self.export_conversation_name = None
        self.export_conversation = None
        self.export_username = None
        self.export_user_id = None
        self.start_conversation_button_text = None
        self.add_message_button_text = None
        self.message_entry = None
        self.message = None
        self.first_name = None
        self.subject = None
        self.mode = None
        self.conversations_by_username = None
        self.conversations_by_mode = None
        self.formatted_conversation = None
        self.path = os.path.join(os.getcwd(), 'Exported Conversations')
        self.root = root
        self.backend = Backend()
        self.previous_conversation_loaded = False
        self.previous_conversations_loaded = False
        self.started_conversation = False
        self.root.title("FGCU TutorTech")
        self.root.iconbitmap('images/icon.ico')
        self.root.state('zoomed')

        self.main_frame = tb.Frame(self.root)
        self.data_menu = None
        self.start_frame = None

        self.show_start_frame()

    def show_start_frame(self):
        """Show the start frame."""
        if self.main_frame:
            self.main_frame.pack_forget()  # Hide the main frame if it exists
        self.start_frame = StartFrame(self.root, self.on_start)

    def on_start(self, first_name, subject, mode):
        """
        Handle the start event.

        Args:
            first_name: The first name entered by the user.
            subject: The selected subject.
            mode: The selected mode.
        """
        self.first_name = first_name
        self.subject = subject
        self.mode = mode
        self.backend.set_subject(subject)
        self.backend.set_mode(mode)
        print(first_name, subject, mode)
        self.backend.check_username(first_name)
        self.backend.set_username(first_name)
        self.backend.create_conversation_name()  # initialize conversation name
        if self.start_frame:
            self.start_frame.frame.pack_forget()  # Hide the start frame
        self.show_main_frame()

    def show_main_frame(self):
        """Show the main frame."""
        self.main_frame = tb.Frame(self.root)
        self.main_frame.pack(expand=True, fill=tb.BOTH)

        # Create a new frame to hold the info_label and mode_menu
        self.info_frame = tb.Frame(self.main_frame)
        self.info_frame.pack(side=tb.TOP, fill=tb.X, pady=5, padx=5)

        # Create the info_label and pack it to the left side of the info_frame
        self.info_label = tb.Label(self.info_frame, text=f'Name: {self.first_name}', font=('Helvetica', 12))
        self.info_label.pack(side=tb.LEFT)

        # Create the mode_menu and pack it to the right of the info label
        style = tb.Style()
        style.configure('TMenubutton', font=('Helvetica', 12), width=20)
        self.mode_menu = tb.Menubutton(self.info_frame, text=f'{self.mode}', direction="below", style='secondary')
        self.mode_menu.menu = tb.Menu(self.mode_menu, tearoff=False)
        self.mode_menu.configure(menu=self.mode_menu.menu)
        self.mode_menu.menu.configure(font=('Helvetica', 12))
        modes = ['Tutor', 'Tutee', 'Generate Conversation']
        for mode in modes:
            self.mode_menu.menu.add_command(label=mode, command=lambda m=mode: self.change_mode(m))
        self.mode_menu.pack(side=tb.LEFT, padx=5)

        if self.first_name == 'CAA Staff':
            self.view_data_analysis_button = tb.Button(self.info_frame, text='View Data Analysis',
                                                       command=self.data_analysis_menu, style='secondary')
            self.view_data_analysis_button.pack(side=tb.RIGHT, padx=5)

            self.evaluate_button = tb.Button(self.info_frame, text='Evaluate Conversation', command=self.evaluate)
            self.evaluate_button.pack(side=tb.RIGHT, padx=5)

        # Create conversation display area
        self.conversation_frame = tb.Frame(self.main_frame, padding=(10, 10, 0, 10))
        self.conversation_frame.pack(expand=True, fill=tb.BOTH, side=tb.RIGHT)

        # Create conversation display area
        self.conversation_frame_inner = tb.Frame(self.conversation_frame)
        self.conversation_frame_inner.pack(expand=True, fill=tb.BOTH)

        self.conversation_text = tb.Text(self.conversation_frame_inner, wrap=tb.WORD, state='disabled',
                                         height=20, width=100, font=('Helvetica', 12))
        self.conversation_text.pack(side=tb.LEFT, fill=tb.BOTH, expand=True)

        self.scrollbar = tb.Scrollbar(self.conversation_frame_inner, orient=tb.VERTICAL,
                                      command=self.conversation_text.yview, style='primary-round')
        self.scrollbar.pack(side=tb.RIGHT, fill=tb.Y, padx=5)
        self.conversation_text.config(yscrollcommand=self.scrollbar.set)

        # Create a frame to hold the entry box and button
        self.input_frame = tb.Frame(self.conversation_frame)
        self.input_frame.pack(side=tb.BOTTOM, fill=tb.X, padx=10, pady=10)

        # Add the delete button
        self.delete_button = tb.Button(self.input_frame, text="Delete Conversation", command=self.delete_conversation,
                                       style='secondary')
        self.delete_button.pack(side=tb.RIGHT, padx=5)

        if self.first_name != 'CAA Staff':
            # Add the entry box
            if self.mode != 'Generate Conversation':
                self.message_entry = tb.Text(self.input_frame, wrap=tb.WORD, height=3, width=45, font=('Helvetica', 12))
                self.message_entry.bind("<Return>", lambda event: self.add_message())
                self.message_entry.pack(side=tb.LEFT, padx=(0, 5))
            # Add the enter button
            if self.mode == 'Generate Conversation':
                self.add_message_button_text = 'Generate New Messages'
            else:
                self.add_message_button_text = 'Enter'
            self.add_message_button = tb.Button(self.input_frame, text=self.add_message_button_text,
                                                command=self.add_message, style='primary')
            self.add_message_button.pack(side=tb.LEFT, padx=(5, 40))

            # Configure column widths to make buttons appear to the right
            self.input_frame.columnconfigure(2, weight=1)  # This will expand empty space between buttons

            # Add the save button
            self.save_button = tb.Button(self.input_frame, text="Save Conversation", command=self.save_conversation)
            self.save_button.pack(side=tb.RIGHT, padx=(5, 5))

            # Add start conversation button
            if self.mode == 'Generate Conversation':
                self.start_conversation_button_text = 'Generate Conversation'
            else:
                self.start_conversation_button_text = 'Start Conversation'
            self.start_conversation_button = tb.Button(self.input_frame, text=self.start_conversation_button_text,
                                                       command=self.start_conversation, style='primary')
            self.start_conversation_button.pack(side=tb.RIGHT, padx=(10, 5))

        # Create a frame to hold the TreeView
        self.tree_frame = tb.Frame(self.main_frame, padding=(10, 10, 10, 20))
        self.tree_frame.pack(side=tb.LEFT, fill=tb.BOTH)

        # Create the TreeView
        self.tree = tb.Treeview(self.tree_frame, columns=('conversation',), style='primary')
        self.tree.heading('#0', text='Previous Conversations', anchor='w')
        self.tree.column('#0', width=300)
        self.tree.pack(expand=True, fill=tb.BOTH)

        # Create the frame for exit and export buttons
        self.exit_and_export_frame = tb.Frame(self.tree_frame, padding=(10, 10, 10, 20))
        self.exit_and_export_frame.pack(side=tb.BOTTOM, fill=tb.X)

        # Create the Exit button
        self.exit_button = tb.Button(self.exit_and_export_frame, text="Exit", command=self.exit, style='secondary')
        self.exit_button.pack(side=tb.LEFT, anchor='sw', padx=(0, 10), pady=5)

        # Create the Export button
        self.export_button = tb.Button(self.exit_and_export_frame, text='Export', command=self.export, style='primary')
        self.export_button.pack(side=tb.RIGHT, anchor='se', padx=(10, 0), pady=5)

        # Load previous conversations into the TreeView
        self.load_previous_conversations()

        # Bind the tree selection event to load the selected conversation
        self.tree.bind('<<TreeviewSelect>>', self.load_selected_conversation)

    def change_mode(self, mode):
        if self.started_conversation:
            messagebox.showerror('Error', 'Cant\'t change modes')
            return
        self.mode_menu.configure(text=mode)
        self.mode = mode
        self.backend.set_mode(mode)
        self.main_frame.pack_forget()
        self.show_main_frame()
        self.backend.create_conversation_name()

    def evaluate(self):
        print("Previous Conversation Loaded: ", self.previous_conversation_loaded)
        if self.data_menu is None:
            messagebox.showerror("Error", "Must have Data Analysis Menu open")
            return
        elif not self.previous_conversation_loaded:
            messagebox.showerror("Error", "Must select previous conversation to evaluate")
            return
        else:
            self.backend.set_evaluate_conversation(True)
            api_response = self.backend.generate_response(self.formatted_conversation, self.export_user_id,
                                                      self.export_username, self.export_conversation_name)
#             api_response = """To Zach: 1. Positives:
#    - The tutor guided the tutee in setting up the equation correctly by using the formula distance = speed x time.
#    - The tutor confirmed the tutee's answer after the calculation.
#
# 2. Suggestions for Improvement:
#    - The tutor could have asked the tutee to provide an explanation of how they arrived at the final answer to ensure their understanding of the concept.
#    - It would have been beneficial for the tutee's learning if the tutor had prompted the tutee to solve similar problems or provide more practice questions to reinforce the concept.
#
# 3. Confidence: 95%
#             """
            # Extracting confidence percentage using regular expression
            confidence_percentage = re.search(r'Confidence\D+(\d+)%', api_response)
            if confidence_percentage:
                confidence = int(confidence_percentage.group(1))
                # Update meter widget with confidence percentage
                self.data_menu.confidence_meter.configure(amountused=confidence)

            # Removing all numbering except "1." and "2."
            response = re.sub(r'\b(?!1\.|2\.)\d+\.', '', api_response)
            response = re.sub(r'Confidence\D+\d+%', '', response)

            self.data_menu.evaluation_text.config(state='normal')  # Set state to normal to allow editing
            self.data_menu.evaluation_text.delete(1.0, tb.END)  # Clear existing conversation
            self.data_menu.evaluation_text.insert(tb.END, response)  # Insert selected conversation
            self.data_menu.evaluation_text.config(state='disabled')  # Set state to disabled to disable editing
            self.backend.set_evaluate_conversation(False)

    def data_analysis_menu(self):
        # Create Data Analysis Menu
        self.conversations_by_username = self.backend.conversations_by_username
        self.data_menu = DataAnalysisMenu(self.main_frame, self.backend, self.first_name,
                                          list(self.conversations_by_username.keys()),
                                          self.path)

    def start_conversation(self):
        """Start a new conversation."""
        if self.previous_conversation_loaded:
            yesno = messagebox.askyesno("Start New Conversation",
                                        "Are you sure you want to start a new conversation?")
            if yesno:
                self.clear_conversation()
            else:
                return

        self.message = 'Start'
        self.started_conversation = True
        self.add_message()

    def add_message(self):
        """Add messages to the conversation."""
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
                self.conversation_text.insert(tb.END, f"{self.first_name}: {message}\n")
                response = self.backend.generate_response(message, user_id, self.first_name, conversation_name)
                self.conversation_text.insert(tb.END, f"{self.subject} {self.mode}: {response}\n\n")

            # Clear the entry box after adding the message
            self.message_entry.delete(1.0, tb.END)

        self.conversation_text.config(state='disabled')

        # Scroll to the bottom of the conversation text widget
        self.conversation_text.see(tb.END)

        return 'break'  # move cursor back to first line

    def save_conversation(self):
        """Save the conversation."""
        self.started_conversation = False
        self.previous_conversations_loaded = False
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
        """Export the conversation."""
        if self.export_username is None or self.export_conversation_name is None:
            messagebox.showerror("Error", "Must select previous conversation to export")
            return

        def on_button_click(export_format):
            # Call the backend function to export the conversation
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
        """
        Set the export directory.

        Args:
            label_widget: The label widget to display the selected directory.
        """
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
        """
        Check if the conversation is empty.

        Returns:
            bool: True if the conversation is empty, False otherwise.
        """
        # Get the content of the conversation text widget
        conversation_content = self.conversation_text.get("1.0", tb.END).strip()
        # Check if the content is empty
        return not conversation_content

    def delete_conversation(self):
        """Delete the conversation."""
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
        """Load the previously saved conversations"""
        self.started_conversation = False
        # Clear existing items in the TreeView
        for item in self.tree.get_children():
            self.tree.delete(item)

        if self.first_name == 'CAA Staff':
            if not self.previous_conversations_loaded:
                print("here 1")
                self.conversations_by_username = self.backend.retrieve_conversations_by_username(self.first_name)
            for username, data in self.conversations_by_username.items():
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
            if not self.previous_conversations_loaded:
                print("here 2")
                self.conversations_by_mode = self.backend.retrieve_conversations_by_mode(user_id)
            # Insert mode folders and conversations into the TreeView
            for mode, conversations in self.conversations_by_mode.items():
                if mode == 'Generate Conversation':
                    mode_item = self.tree.insert('', 'end', text="Generated Conversations")
                else:
                    mode_item = self.tree.insert('', 'end', text=f"{mode} Conversations")
                for conversation in conversations:
                    self.tree.insert(mode_item, 'end', text=conversation)

        self.tree.tag_configure('big_font', font=('Helvetica', 10))
        for item in self.tree.get_children():
            self.tree.item(item, tags=('big_font',))
        self.previous_conversations_loaded = True

    def load_selected_conversation(self, event):
        """Load the selected conversation"""
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
        print("conversation name from tree", conversation_name)
        if conversation_name in ["Tutee Conversations", "Tutor Conversations", "Generated Conversations"]:
            print("returned")
            return
        # Retrieve the conversation from the backend
        self.export_conversation_name = conversation_name
        self.export_username = username
        self.export_user_id = user_id
        conversation = self.backend.retrieve_previous_conversation(user_id, conversation_name)
        if conversation:
            self.previous_conversation_loaded = True
            # Format the conversation for display
            self.formatted_conversation = self.backend.format_conversation(conversation)
            print("formatting done")
            # Display the selected conversation in the conversation text widget
            self.conversation_text.config(state='normal')  # Set state too normal to allow editing
            self.conversation_text.delete(1.0, tb.END)  # Clear existing conversation
            self.conversation_text.insert(tb.END, self.formatted_conversation)  # Insert selected conversation
            self.conversation_text.config(state='disabled')  # Set state to disabled to disable editing

    def clear_conversation(self):
        """Clear the conversation."""
        # Clear the conversation display area
        self.conversation_text.config(state='normal')  # Set state too normal to allow editing
        self.conversation_text.delete(1.0, tb.END)  # Clear existing conversation
        self.conversation_text.config(state='disabled')  # Set state to disabled to disable editing

    def exit(self):
        """Exit the program and show the Start Frame"""
        self.previous_conversations_loaded = False
        self.clear_conversation()
        self.show_start_frame()


def start_gui():
    """Start the GUI."""
    root = tb.Window(themename='fgcu')
    gui = GUI(root)
    root.mainloop()
