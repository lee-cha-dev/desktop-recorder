import logging
import os
import datetime


class CustomLogger:
    def __init__(self, log_name='application.log'):
        self.log_name = log_name
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Create log directory structure based on current datetime
        datetime_string = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_directory = os.path.join('logs', f'log{datetime_string}')
        os.makedirs(self.log_directory, exist_ok=True)

        # Create and add file handler
        log_path = os.path.join(self.log_directory, self.log_name)
        self.file_handler = logging.FileHandler(log_path)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    def log(self, message):
        self.logger.info(message)

    def save(self):
        # Close the file handler and save the log file
        self.logger.removeHandler(self.file_handler)
        self.file_handler.close()
