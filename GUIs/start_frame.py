import os
import ttkbootstrap as tb
from tkinter import messagebox, simpledialog
from PIL import ImageTk, Image
from cryptography.fernet import Fernet
import base64


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
