import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QWidget
import json
import datetime
import pytz
import win32file, win32con

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Set time on photo dowanload from google photos')
        self.setGeometry(250, 50, 1400, 900)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Layout
        layout = QVBoxLayout()

        # Buttons
        self.button_choose_folder = QPushButton('Choose Folder', self)
        self.button_choose_folder.clicked.connect(self.choose_folder)
        layout.addWidget(self.button_choose_folder)

        self.button_start_function = QPushButton('Start Function', self)
        self.button_start_function.clicked.connect(self.start_set_time)
        layout.addWidget(self.button_start_function)
        
        # Log Text Boxes
        self.logOK = QTextEdit(self)
        self.logFail = QTextEdit(self)
        self.logOK.setReadOnly(True)
        self.logFail.setReadOnly(True)
        layout.addWidget(self.logOK)
        layout.addWidget(self.logFail)

        # Set the layout to the central widget
        self.central_widget.setLayout(layout)

    def choose_folder(self):
        self.folder_path = QFileDialog.getExistingDirectory(self, 'Choose Folder', os.path.expanduser("~"))
        if self.folder_path:
            # Clear the log and error text widgets
            self.logOK.clear()
            self.logFail.clear()
            self.log_message(f"Chosen directory: {self.folder_path}")
        else:
            self.log_message("No directory chosen.")

    def start_set_time(self):
        if self.folder_path:
            self.process_directory(self.folder_path)
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
        logfiledate = datetime.datetime.now().strftime('%Y%m%d')
        log_entry = f"[{timestamp}] {message}\n"

        if is_error:
            self.logFail.insertPlainText(log_entry)
        else:
            self.logOK.insertPlainText(log_entry)

        # Save log entry to a file
        log_file_path = "error_"+logfiledate+".log" if is_error else "info_"+logfiledate+".log"
        with open(log_file_path, "a") as log_file:
            log_file.write(log_entry)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
