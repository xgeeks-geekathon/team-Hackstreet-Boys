import os
from tkinter import filedialog, ttk
import tkinter as tk


class Gradebook(tk.Frame):
    def __init__(self, master_window):
        super().__init__(master_window)
        self.grid(sticky="nsew")

        # Adjust background colors
        self.configure(bg="white")
        self.create_progressbar()
        self.create_file_widgets()

        # Create a frame for each table
        self.table_frame1 = ttk.Frame(self)
        self.table_frame1.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.table_frame2 = ttk.Frame(self)
        self.table_frame2.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        # Create the first table with a blue layout
        self.table1 = self.create_table_frame("Table 1", [], self.table_frame1, bg="#85C1E9")

        # Create the second table with a blue layout
        self.table2 = self.create_table_frame("Table 2", [], self.table_frame2, bg="#85C1E9")

        # Create the "Generate Tests" button
        generate_tests_btn = ttk.Button(
            master=self,
            text="Generate Tests",
            command=self.generate_tests,
            width=15,
        )
        generate_tests_btn.grid(row=2, column=0, columnspan=2, pady=(5, 0), sticky="ew")

        # Create the "Choose Output Directory" button
        choose_output_dir_btn = ttk.Button(
            master=self,
            text="Choose Output Directory",
            command=self.choose_output_directory,
            width=20,
        )
        choose_output_dir_btn.grid(row=3, column=0, columnspan=2, pady=(5, 0), sticky="ew")

        # Variables to store output directory
        self.output_directory_var = tk.StringVar(value="No directory chosen")

        # Label to display the chosen output directory
        output_dir_label = ttk.Label(
            master=self,
            textvariable=self.output_directory_var,
            style="TLabel",
            anchor="w",
        )
        output_dir_label.grid(row=4, column=0, columnspan=2, pady=(5, 10), sticky="ew")

        # Adjust row and column weights
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def create_progressbar(self):
        self.progress_var = tk.DoubleVar()
        progressbar = ttk.Progressbar(
            master=self,
            orient="horizontal",
            mode="determinate",
            maximum=100,
            variable=self.progress_var,
        )
        progressbar.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="ew")

    def create_file_widgets(self):
        file_container = ttk.Frame(self)
        file_container.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 5))

        load_file_btn = ttk.Button(
            master=file_container,
            text="Load File",
            command=self.load_file,
            width=10,
        )
        load_file_btn.grid(row=0, column=0, padx=5)

        self.file_name_var = tk.StringVar(value="")
        file_name_entry = ttk.Entry(
            master=file_container,
            textvariable=self.file_name_var,
            state="readonly",  # Read-only to display the file name
        )
        file_name_entry.grid(row=0, column=1, padx=5, sticky="ew")

    def load_file(self):
        filenames = filedialog.askopenfilenames(
            initialdir="/",
            title="Select files",
            filetypes=(
                ("Allowed code files", "*.cpp;*.js;*.c;*.py"),
                ("All Files", "*.*")
            )
        )

        if filenames:
            # Display the selected file names in the entry widget
            self.file_name_var.set("; ".join(os.path.basename(file) for file in filenames))

            # Display the loaded file name on Table 1
            loaded_name = os.path.basename(filenames[0])
            self.table1.insert("", "end", values=(loaded_name,))

    def generate_tests(self):
        # Get items from Table 1
        items = self.table1.get_children()
        total_items = len(items)

        # Update progress bar based on Table 1 completion
        for i, item in enumerate(items, start=1):
            values = self.table1.item(item, "values")
            self.table2.insert("", "end", values=values)

            # Update progress bar
            completion_percentage = (i / total_items) * 100
            self.progress_var.set(completion_percentage)
            self.update_idletasks()

    def create_table_frame(self, title, data, table_frame, bg):
        table_label = ttk.Label(table_frame, text=title, font=("Helvetica", 16), background=bg)
        table_label.grid(row=0, column=0, pady=5, sticky="ew")

        coldata = [
            {"text": "Name"},
        ]

        tree = ttk.Treeview(
            master=table_frame,
            columns=[col["text"] for col in coldata],
            show="headings",
        )

        for col in coldata:
            tree.heading(col["text"], text=col["text"])
            tree.column(col["text"], width=150)  # Adjust the width as needed

        tree.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(1, weight=1)
        return tree

    def choose_output_directory(self):
        output_directory = filedialog.askdirectory(title="Choose Output Directory")
        if output_directory:
            self.output_directory_var.set(output_directory)


if __name__ == "__main__":
    app = tk.Tk()
    app.title("Gradebook")
    app.geometry("800x600")  # Set an initial window size
    Gradebook(app)
    app.mainloop()
