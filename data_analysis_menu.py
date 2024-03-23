import ttkbootstrap as tb
import os
import io
from PIL import Image, ImageTk


class DataAnalysisMenu:
    def __init__(self, master, backend, first_name, tutor_names, cwd):
        self.master = master
        self.backend = backend
        self.first_name = first_name
        self.tutor_names = tutor_names
        self.cwd = cwd
        self.top = None
        self.selected_mode = None
        self.selected_tutor = None
        self.diagram_frame = None
        self.controls_frame = None
        self.diagram = None
        self.total_button = None
        self.totals_by_mode_button = None
        self.totals_by_tutor_button = None
        self.export_to_excel_button = None
        self.mode_menu = None
        self.tutor_menu = None
        self.plot_image_tk = None
        self.data_analysis_menu()

    def data_analysis_menu(self):
        self.top = tb.Toplevel()
        self.top.title("Data Analysis")
        self.top.state('zoomed')

        # Set minimum size for the window
        self.top.minsize(640, 480)

        # Create the main frame
        main_frame = tb.Frame(self.top)
        main_frame.pack(fill=tb.BOTH, expand=True)

        # Create frames
        self.diagram_frame = tb.Frame(main_frame, padding=(50, 50, 50, 50))  # Add padding here
        self.diagram_frame.pack(side=tb.TOP, fill=tb.BOTH, expand=True)

        self.controls_frame = tb.Frame(main_frame)
        self.controls_frame.pack(side=tb.BOTTOM, fill=tb.X)

        # Diagram frame
        self.diagram = tb.Label(self.diagram_frame, relief='solid', borderwidth=2)
        self.diagram.pack(fill=tb.BOTH, expand=True)

        # Controls frame
        self.total_button = tb.Button(self.controls_frame, text="Total Conversations",
                                      command=self.view_total_conversations)
        self.total_button.pack(side=tb.LEFT, padx=5, pady=5)

        self.mode_menu = tb.Menubutton(self.controls_frame, text='Select Mode', direction="below", style='secondary')
        self.mode_menu.menu = tb.Menu(self.mode_menu, tearoff=False)
        self.mode_menu.configure(menu=self.mode_menu.menu)
        self.mode_menu.menu.configure(font=('Helvetica', 12))
        modes = ['Tutor', 'Tutee', 'Generate Conversation']
        for mode in modes:
            self.mode_menu.menu.add_command(label=mode, command=lambda m=mode: self.select_mode(m))
        self.mode_menu.pack(side=tb.LEFT, padx=5)

        self.totals_by_mode_button = tb.Button(self.controls_frame, text="Plot Totals by Mode",
                                               command=self.view_total_conversations_by_mode)
        self.totals_by_mode_button.pack(side=tb.LEFT, padx=5)

        self.tutor_menu = tb.Menubutton(self.controls_frame, text='Select Tutor', direction="below", style='secondary')
        self.tutor_menu.menu = tb.Menu(self.tutor_menu, tearoff=False)
        self.tutor_menu.configure(menu=self.tutor_menu.menu)
        self.tutor_menu.menu.configure(font=('Helvetica', 12))
        for tutor in self.tutor_names:
            self.tutor_menu.menu.add_command(label=tutor, command=lambda t=tutor: self.select_tutor(t))
        self.tutor_menu.pack(side=tb.LEFT, padx=5)

        self.totals_by_tutor_button = tb.Button(self.controls_frame, text="Plot Totals by Tutor",
                                                command=self.view_total_conversations_by_tutor)
        self.totals_by_tutor_button.pack(side=tb.LEFT, padx=5)

        self.export_to_excel_button = tb.Button(self.controls_frame, text="Export To Excel",
                                                command=self.export_to_excel)
        self.export_to_excel_button.pack(side=tb.LEFT, padx=5)

        # Make the pop-up window modal (prevent interaction with other windows)
        self.top.grab_set()

        # Wait for the pop-up window to be closed before returning
        self.top.wait_window()

    def select_mode(self, mode):
        self.selected_mode = mode
        self.mode_menu.configure(text=mode)

    def select_tutor(self, tutor):
        self.selected_tutor = tutor
        self.tutor_menu.configure(text=tutor)

    def view_total_conversations(self):
        self.backend.make_total_conversations_per_mode()
        encrypted_plot_image_path = os.path.join(os.getcwd(), f'{self.first_name} Diagrams',
                                                 'total_number_of_conversations_per_mode_plot.enc')
        self.plot_diagram(encrypted_plot_image_path)

    def view_total_conversations_by_mode(self):
        self.backend.make_total_conversations_by_mode_per_tutor(self.selected_mode)
        encrypted_plot_image_path = os.path.join(os.getcwd(), f'{self.first_name} Diagrams',
                                                 f'total_number_of_{self.selected_mode}_conversations_per_tutor_plot.enc')
        self.plot_diagram(encrypted_plot_image_path)

    def view_total_conversations_by_tutor(self):
        self.backend.make_total_conversations_by_tutor(self.selected_tutor)
        encrypted_plot_image_path = os.path.join(os.getcwd(), f'{self.first_name} Diagrams',
                                                 f'total_number_of_conversations_by_tutor_{self.selected_tutor}_plot.enc')
        self.plot_diagram(encrypted_plot_image_path)

    def plot_diagram(self, encrypted_path):
        if os.path.exists(encrypted_path):
            # Decrypt the image
            with open(encrypted_path, 'rb') as file:
                encrypted_image_data = file.read()
            decrypted_image_data = self.backend.decrypt_data(encrypted_image_data)

            if decrypted_image_data:
                try:
                    # Load the decrypted image directly into memory
                    image_stream = io.BytesIO(decrypted_image_data)
                    plot_image = Image.open(image_stream)

                    # Display the image using Tkinter
                    self.plot_image_tk = ImageTk.PhotoImage(plot_image)
                    self.diagram.configure(image=self.plot_image_tk)
                except Exception as e:
                    # If an error occurs during image loading or decryption, show an error message
                    error_label = tb.Label(self.top, text=f"Error: {str(e)}")
                    print(str(e))
                    error_label.pack()
            else:
                # If decryption fails, show an error message
                error_label = tb.Label(self.top, text="Error: Failed to decrypt the image!")
                error_label.pack()
        else:
            # If the encrypted plot image doesn't exist, show an error message
            error_label = tb.Label(self.top, text="Error: Encrypted plot image not found!")
            error_label.pack()

    def export_to_excel(self):
        pass
