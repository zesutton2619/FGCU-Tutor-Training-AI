import ttkbootstrap as tb
from tkinter import messagebox
import os
import io
from PIL import Image, ImageTk


class DataAnalysisDashboard:
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
        self.evaluation_response_text = None
        self.evaluation_text = None
        self.quality_meter = None
        self.confidence_meter = None
        self.diagram_text = None
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
        self.top.title("Data Analysis Dashboard")
        self.top.state('zoomed')

        # Set minimum size for the window
        self.top.minsize(640, 480)

        # Create the main frame
        main_frame = tb.Frame(self.top)
        main_frame.pack(fill=tb.BOTH, expand=True)

        # Create frames
        self.diagram_frame = tb.Frame(main_frame)  # Add padding here
        self.diagram_frame.pack(side=tb.TOP, fill=tb.BOTH, expand=True)

        self.controls_frame = tb.Frame(main_frame)
        self.controls_frame.pack(side=tb.BOTTOM, fill=tb.X, pady=10, expand=True)

        # Diagram frame
        self.diagram_text = tb.Label(self.diagram_frame, text='Diagram', font=('Helvetica', 14))
        self.diagram_text.grid(row=0, column=0, pady=5)

        self.diagram = tb.Label(self.diagram_frame, relief='solid', borderwidth=2, width=125)
        self.diagram.grid(row=1, column=0, padx=(25, 10), pady=(20, 40))

        self.evaluation_response_text = tb.Label(self.diagram_frame, text='Evaluation Response', font=('Helvetica', 14))
        self.evaluation_response_text.grid(row=0, column=1, pady=5)

        self.evaluation_text = tb.Text(self.diagram_frame, wrap=tb.WORD, state='disabled', width=60, height=25,
                                       font=('Helvetica', 14))
        self.evaluation_text.grid(row=1, column=1)

        meter_frame = tb.Frame(self.diagram_frame)
        meter_frame.grid(row=2, column=1, columnspan=2, pady=(20, 10), sticky="ew")

        self.quality_meter = tb.Meter(meter_frame, subtext='Quality', textright='%',
                                      amountused=0, amounttotal=100, metersize=150,
                                      bootstyle='secondary', subtextstyle='primary', subtextfont=('Helvetica', 12))
        self.quality_meter.grid(row=0, column=0, padx=(250, 50))

        self.confidence_meter = tb.Meter(meter_frame, subtext='Confidence', textright='%',
                                         amountused=0, amounttotal=100, metersize=150,
                                         bootstyle='secondary', subtextstyle='primary', subtextfont=('Helvetica', 12))
        self.confidence_meter.grid(row=0, column=1, padx=(50, 250))

        # Controls frame
        self.total_button = tb.Button(self.controls_frame, text="Total Conversations",
                                      command=self.view_total_conversations)
        self.total_button.grid(row=0, column=0, padx=(50, 0))

        self.mode_menu = tb.Menubutton(self.controls_frame, text='Select Mode', direction="above", style='secondary')
        self.mode_menu.menu = tb.Menu(self.mode_menu, tearoff=False)
        self.mode_menu.configure(menu=self.mode_menu.menu)
        self.mode_menu.menu.configure(font=('Helvetica', 12))
        modes = ['Tutor', 'Tutee', 'Generate Conversation']
        for mode in modes:
            self.mode_menu.menu.add_command(label=mode, command=lambda m=mode: self.select_mode(m))
        self.mode_menu.grid(row=0, column=1, padx=10, pady=5)

        self.tutor_menu = tb.Menubutton(self.controls_frame, text='Select Tutor', direction="above", style='secondary')
        self.tutor_menu.menu = tb.Menu(self.tutor_menu, tearoff=False)
        self.tutor_menu.configure(menu=self.tutor_menu.menu)
        self.tutor_menu.menu.configure(font=('Helvetica', 12))
        for tutor in self.tutor_names:
            self.tutor_menu.menu.add_command(label=tutor, command=lambda t=tutor: self.select_tutor(t))
        self.tutor_menu.grid(row=0, column=2, padx=10, pady=5)

        self.totals_by_mode_button = tb.Button(self.controls_frame, text="Plot Totals by Mode",
                                               command=self.view_total_conversations_by_mode)
        self.totals_by_mode_button.grid(row=1, column=1, padx=10, pady=(0, 20))

        self.totals_by_tutor_button = tb.Button(self.controls_frame, text="Plot Totals by Tutor",
                                                command=self.view_total_conversations_by_tutor)
        self.totals_by_tutor_button.grid(row=1, column=2, padx=10, pady=(0, 20))

        self.export_to_excel_button = tb.Button(self.controls_frame, text="Export To Excel",
                                                command=self.export_to_excel)
        self.export_to_excel_button.grid(row=0, column=3, padx=10)

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
        if self.selected_mode is None:
            messagebox.showerror("Error", "Must select mode")
            return
        # Call the backend method to generate the plot
        self.backend.make_total_conversations_by_mode_per_tutor(self.selected_mode)

        # Construct the filename based on the selected mode
        if self.selected_mode == "Generate Conversation":
            filename = f'total_number_of_generate_conversation_conversations_per_tutor_plot.enc'
        else:
            filename = f'total_number_of_{self.selected_mode}_conversations_per_tutor_plot.enc'

        # Construct the full path to the encrypted plot image
        encrypted_plot_image_path = os.path.join(os.getcwd(), f'{self.first_name} Diagrams', filename)

        # Display the plot
        self.plot_diagram(encrypted_plot_image_path)

    def view_total_conversations_by_tutor(self):
        if self.selected_tutor is None:
            messagebox.showerror("Error", "Must select tutor")
            return
        self.backend.make_total_conversations_by_tutor(self.selected_tutor)
        encrypted_plot_image_path = os.path.join(os.getcwd(), f'{self.first_name} Diagrams',
                                                 f'total_number_of_conversations_by_tutor_'
                                                 f'{self.selected_tutor}_plot.enc')
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
        export_path = self.backend.export_conversations_to_excel()
        messagebox.showinfo("Exported Path", f"Exported to: {export_path}")
