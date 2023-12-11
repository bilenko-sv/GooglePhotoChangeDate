import os
import json
import datetime
import pytz
import win32file, win32con
import tkinter as tk
from tkinter import filedialog

class MyApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Set time on photo dowanload from google photos")
        self.master.geometry('1400x900+250+50')
        # Choose directory button
        self.create_widgets()

        # Store chosen directory
        self.chosen_dir = None

    def create_widgets(self):
        # Choose directory button

        # Log file output with scrollbar
        self.log_text = self.create_text_widget(25, 150)
        self.log_scrollbar = self.create_scrollbar(self.log_text)
        self.log_text.configure(yscrollcommand=self.log_scrollbar.set)
        self.log_scrollbar.pack(side="right", fill="y")
        self.log_text.pack(expand=True, fill="x",pady=50)

        # Error output with scrollbar
        self.error_text = self.create_text_widget(25, 150, fg="red")
        self.error_scrollbar = self.create_scrollbar(self.error_text)
        self.error_text.configure(yscrollcommand=self.error_scrollbar.set)
        self.error_scrollbar.pack(side="right", fill="y")
        self.error_text.pack(expand=True, fill="both")
        
        self.choose_dir_button = tk.Button(
            self.master, text="Choose Directory", command=self.choose_directory,
            padx=100, pady=12
        )
        self.choose_dir_button.place(x=20, y=10)

        # Set time button
        self.set_time_button = tk.Button(
            self.master, text="Set Time", command=self.set_time,
            padx=100, pady=12
        )
        self.set_time_button.place(x=360, y=10)

    def create_text_widget(self, height, width, **kwargs):
        text_widget = tk.Text(self.master, height=height, width=width, **kwargs)
        text_widget.pack_propagate(False)  # Prevents the Text widget from resizing itself
        return text_widget

    def create_scrollbar(self, text_widget):
        scrollbar = tk.Scrollbar(self.master, command=text_widget.yview)
        return scrollbar

    def choose_directory(self):
        self.chosen_dir = filedialog.askdirectory()
        if self.chosen_dir:
            # Clear the log and error text widgets
            self.log_text.delete(1.0, tk.END)
            self.error_text.delete(1.0, tk.END)
            self.log_message(f"Chosen directory: {self.chosen_dir}")
        else:
            self.log_message("No directory chosen.")

    def set_time(self):
        if self.chosen_dir:
            self.process_directory(self.chosen_dir)
        else:
            self.log_message("Please choose a directory first.")

    def process_directory(self, directory_path):
        self.log_message(f"Processing files in directory: {directory_path}")

        for root, dirs, files in os.walk(directory_path):
            for file_name in files:
                if file_name.endswith('.json'):
                    json_file_path = os.path.join(root, file_name)
                    self.process_json_file(json_file_path, root)

    def process_json_file(self, file_path, dir_path):
        try:
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
                title = os.path.splitext(os.path.basename(file_path))[0]
                photo_taken_timestamp = data.get('photoTakenTime', {}).get('timestamp')
                formatted_date = datetime.datetime.utcfromtimestamp(int(photo_taken_timestamp))
                log_message = f"File not found000000: {title}"
                if title:
                    file_name = os.path.join(dir_path, title)

                    if os.path.exists(file_name):
                        winter_tz = pytz.timezone('Europe/Kiev')  # UTC+3
                        summer_tz = pytz.timezone('Europe/Kiev')  # UTC+2
                        is_winter = winter_tz.localize(formatted_date).dst() == datetime.timedelta(0)
                        chosen_tz = winter_tz if is_winter else summer_tz
                        local_datetime = formatted_date.replace(tzinfo=pytz.utc).astimezone(chosen_tz)

                        winfile = win32file.CreateFile(
                            file_name,
                            win32con.GENERIC_WRITE,
                            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
                            None, win32con.OPEN_EXISTING,
                            win32con.FILE_ATTRIBUTE_NORMAL, None)
                        win32file.SetFileTime(winfile, local_datetime, local_datetime, local_datetime)
                        winfile.close()

                        log_message = f"File file_attributes: {file_name} \tset time: {local_datetime}"
                        self.log_message(log_message)

                    else:
                        log_message = f"File not found: {file_name}"
                        self.log_message(log_message, is_error=True)

        except Exception as e:
            log_message = f"Error processing file: {file_path}\nError details: {str(e)}"
            self.log_message(log_message, is_error=True)

    def log_message(self, message, is_error=False):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
#
        if is_error:
            self.error_text.insert(tk.END, log_entry)
        else:
            self.log_text.insert(tk.END, log_entry)


    def log_message(self, message, is_error=False):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"

        if is_error:
            self.error_text.insert(tk.END, log_entry)
        else:
            self.log_text.insert(tk.END, log_entry)

        # Save log entry to a file
        log_file_path = "error_log.txt" if is_error else "info_log.txt"
        with open(log_file_path, "a") as log_file:
            log_file.write(log_entry)

if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()