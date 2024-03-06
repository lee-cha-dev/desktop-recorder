import subprocess
import time
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
import pyautogui
import logging
import os
from multiprocessing import Process, Value
import ctypes
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener
import pandas as pd
import datetime
from tkinter import font as tkFont, ttk
import wave

from custom_button import CustomButton, ModernButton
from custom_logger import CustomLogger
from custom_combo_box import CustomComboBox


class ScreenRecorder:
    def __init__(self, root):
        self.fps_label = None
        self.fps_option = None
        self.button_frame_bottom = None
        self.button_frame_middle = None
        self.button_frame_top = None
        self.button_frame = None

        self.open_button = None
        self.stop_button = None
        self.pause_button = None
        self.start_button = None

        self.root = root

        self.filename = None
        self.input_filename = None

        self.datetime_string = None
        self.main_directory_path = None
        self.frames_directory_path = None

        self.recording_process = None
        self.input_logging_process = None
        self.start_time = None
        self.frames = []

        self.record_inputs = True
        self.record_video = True
        self.record_frames = True

        self.record_inputs_option = None
        self.record_video_option = None
        self.record_frames_option = None
        self.check_inputs = True
        self.check_video = True
        self.check_frames = True

        self.custom_font = tkFont.Font(family="Helvetica", size=10, weight="bold")
        self.record_inputs_option = None
        self.record_video_option = None
        self.record_frames_option = None

        self.logger = CustomLogger()
        self.logger.log("INFO:Logger has been initialized.")
        
        # Shared values to control recording and pause across processes
        self.recording_flag = Value(ctypes.c_bool, False)
        self.paused_flag = Value(ctypes.c_bool, False)
        self.pause_start_time = Value(ctypes.c_double, 0.0)  # Time when the recording was paused
        self.total_pause_duration = Value(ctypes.c_double, 0.0)  # Total duration of all pauses

        self.setup_ui()

    # Method to toggle pause state
    def toggle_pause(self):
        now = time.time()
        # Calculate pause times and update shared values accordingly
        if not self.paused_flag.value:
            # Recording is being paused
            self.paused_flag.value = True
            self.pause_start_time.value = now
        else:
            # Recording is resuming from pause
            current_pause_duration = now - self.pause_start_time.value
            self.total_pause_duration.value += current_pause_duration
            self.pause_start_time.value = 0  # Reset pause start time
            self.paused_flag.value = False
        self.update_ui_for_pause_state()
        # Update UI based on the new pause state
        pause_text = "Resume" if self.paused_flag.value else "Pause"
        self.pause_button.config(text=pause_text)

    def update_ui_for_pause_state(self):
        pause_text = "Resume" if self.paused_flag.value else "Pause"
        logging.info(f"Recording {'paused' if self.paused_flag.value else 'resumed'}")
        self.pause_button.config(text=pause_text)

    def setup_ui(self):
        self.logger.log("INFO:Setting up UI.")
        self.root.title("Screen Recorder")
        self.root.geometry("325x600")
        self.root.minsize(300, 575)

        self.root.resizable(False, False)
        self.root.configure(background="#141414")

        # Configure the main window's columns and rows
        self.root.columnconfigure(0, weight=1)  # Pane column takes up 20% of the width
        self.root.rowconfigure(0, weight=1)  # Only one row that takes up all the height

        # BUTTON FRAME
        self.button_frame = tk.Frame(self.root, bg="green")
        self.button_frame.grid(row=0, column=0, sticky="nsew")

        # BUTTON FRAME ROW AND COLUMN CONFIGS
        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.rowconfigure(1, weight=8)
        self.button_frame.rowconfigure(2, weight=1)
        self.button_frame.columnconfigure(0, weight=1)

        # INIT AND CONFIG TOP FRAME
        self.button_frame_top = tk.Frame(self.button_frame, bg="#000000")
        self.button_frame_top.grid(row=0, column=0, sticky="nsew")
        self.button_frame_top.rowconfigure(0, weight=5)
        self.button_frame_top.rowconfigure(1, weight=5)
        self.button_frame_top.columnconfigure(0, weight=5)
        self.button_frame_top.columnconfigure(1, weight=5)

        # INIT AND CONFIG MIDDLE FRAME
        self.button_frame_middle = tk.Frame(self.button_frame, bg="#000000")
        self.button_frame_middle.grid(row=1, column=0, sticky="nsew")
        for i in range(10):
            self.button_frame_middle.rowconfigure(i, weight=i)
        self.button_frame_middle.columnconfigure(0, weight=1)

        # INIT AND CONFIG BOTTOM FRAME
        self.button_frame_bottom = tk.Frame(self.button_frame, bg="#000000")
        self.button_frame_bottom.grid(row=2, column=0, sticky="nsew")
        self.button_frame_bottom.rowconfigure(0, weight=3)
        self.button_frame_bottom.rowconfigure(1, weight=3)
        self.button_frame_bottom.rowconfigure(2, weight=3)
        self.button_frame_bottom.columnconfigure(0, weight=1)

        # SETUP THE THREE FRAME'S CHILD ELEMENTS

        # BUTTON FRAME TOP SETUP
        self.start_button = CustomButton(self.button_frame_top, text="Start Recording", command=self.start_recording)
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.pause_button = CustomButton(self.button_frame_top, text="Pause", state="disabled", command=self.toggle_pause)
        self.pause_button.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.stop_button = CustomButton(self.button_frame_top, text="Stop Recording", state="disabled", command=self.stop_recording)
        self.stop_button.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.open_button = CustomButton(self.button_frame_top, text="Open Recording", command=self.open_recording)
        self.open_button.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        # BUTTON FRAME MIDDLE SETUP
        self.fps_label = tk.Label(self.button_frame_middle, text="FPS:", bg="#141414", fg="white",
                                  font=self.custom_font)
        self.fps_label.grid(row=1, column=0, padx=(5, 0), pady=0, sticky="ew")
        # self.fps_option = CustomMessageBox(self.button_frame_middle, message="This is a custom message box.", title="Custom Title")

        # self.fps_option = ttk.Combobox(self.button_frame_middle, values=['5', '10', '15', '20', '24', '30', '60'], state="readonly")
        self.fps_option = CustomComboBox(
            self.button_frame_middle, values=['5', '10', '15', '20', '24', '30', '60'], state="readonly"
        )
        self.fps_option.grid(row=1, column=1, padx=(0, 5), pady=0, sticky="ew")
        self.fps_option.set(24)  # Default value

        # BUTTON FRAME BOTTOM SETUP
        self.record_video_option = CustomButton(
            self.button_frame_bottom,
            text="Capture Video: True",
            command=self.check_video_command
        )
        self.record_video_option.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.record_frames_option = CustomButton(
            self.button_frame_bottom,
            text="Capture Frames: True",
            command=self.check_frames_command
        )
        self.record_frames_option.grid(row=1, column=0, padx=5, pady=0, sticky="nsew")

        self.record_inputs_option = CustomButton(
            self.button_frame_bottom,
            text="Capture Inputs: True",
            command=self.check_inputs_command
        )
        self.record_inputs_option.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

    def check_frames_command(self):
        if self.check_frames is True:
            self.check_frames = False
        else:
            self.check_frames = True

        self.record_frames_option.config(text=f"Capture Frames: {self.check_frames}")

    def check_video_command(self):
        if self.check_video is True:
            self.check_video = False
            self.check_frames = True
            self.check_inputs = True
            self.check_frames_command()
            self.check_inputs_command()

            self.record_frames_option.config(state="disabled")
            self.record_inputs_option.config(state="disabled")
            self.start_button.config(state="disabled")
        else:
            self.check_video = True
            self.check_frames = False
            self.check_inputs = False
            self.check_frames_command()
            self.check_inputs_command()

            self.record_frames_option.config(state="normal")
            self.record_inputs_option.config(state="normal")
            self.start_button.config(state="normal")

        self.record_video_option.config(text=f"Capture Video: {self.check_video}")

    def check_inputs_command(self):
        if self.check_inputs is True:
            self.check_inputs = False
        else:
            self.check_inputs = True
        self.record_inputs_option.config(text=f"Capture Inputs: {self.check_inputs}")

    def generate_file_paths(self):
        # Format the current datetime in a file-friendly way
        self.datetime_string = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.main_directory_path = os.path.join('data', self.datetime_string)
        self.frames_directory_path = os.path.join(self.main_directory_path, 'frames')
        # Create the directories if they do not already exist
        if not os.path.exists(self.main_directory_path):
            os.makedirs(self.main_directory_path)
        if not os.path.exists(self.frames_directory_path):
            os.makedirs(self.frames_directory_path)
        self.filename = os.path.join(self.main_directory_path, 'recording.avi')
        self.input_filename = os.path.join(self.main_directory_path, 'input_logs.csv')
        self.logger.log(f"CONFIG:Paths Generated: [\n{self.frames_directory_path},\n{self.input_filename},\n{self.filename}\n]")

    def start_recording(self):
        if self.recording_process is None or not self.recording_process.is_alive():
            self.record_frames_option.config(state="disabled")
            self.record_inputs_option.config(state="disabled")
            self.record_video_option.config(state="disabled")

            self.logger.log("INFO:Recording Started.")
            self.generate_file_paths()
            self.recording_flag.value = True
            self.paused_flag.value = False
            self.start_time = time.time()
            self.start_background_processes()
            self.update_ui_state(started=True)

    def start_background_processes(self):
        fps = int(self.fps_option.get())
        self.recording_process = Process(target=self.record, daemon=True, args=(self.filename, fps, self.recording_flag, self.paused_flag, self.frames_directory_path, self.check_frames))
        self.input_logging_process = Process(target=self.start_input_logging, daemon=True, args=(
            self.recording_flag, self.input_filename, self.start_time, self.paused_flag, self.pause_start_time, self.total_pause_duration
        ))
        if self.check_video:
            self.recording_process.start()
        if self.check_inputs:
            self.input_logging_process.start()

    def update_ui_state(self, started=False):
        self.logger.log("INFO:UI Updated.")
        if started:
            logging.info("INFO:Recording started")
            self.start_button.config(state="disabled")
            self.pause_button.config(state="normal", text="Pause")
            self.stop_button.config(state="normal")
        else:
            logging.info("INFO:Recording stopped and saved.")
            self.start_button.config(state="normal")
            self.pause_button.config(state="disabled")
            self.stop_button.config(state="disabled")

    def stop_recording(self):
        self.logger.log("INFO:Recording stopped, saving data.")
        if self.recording_process and self.recording_process.is_alive():
            self.recording_flag.value = False
            if self.recording_process is not None and self.check_video:
                self.recording_process.join()
            if self.input_logging_process is not None and self.check_inputs:
                self.input_logging_process.join()
            video_filename = self.filename  # Already defined in start_recording
            self.logger.log(f"INFO:AVI saved. Output saved to {video_filename}")
        elif self.input_logging_process is not None and self.check_inputs:
            print("Inside Elif")
            self.input_logging_process.join()

        self.record_frames_option.config(state="normal")
        self.record_inputs_option.config(state="normal")
        self.record_video_option.config(state="normal")
        print("Outside Elif")
        self.update_ui_state(started=False)


    @staticmethod
    def record(filename, fps, recording_flag, paused_flag, frames_directory_path, check_frames):
        frames = []
        screen_size = pyautogui.size()
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(filename, fourcc, fps, (screen_size.width, screen_size.height))
        while recording_flag.value:
            if not paused_flag.value:
                img = pyautogui.screenshot()
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame)
                out.write(frame)

        # METHOD FOR SAVING THE ACTUAL IMAGES (SAVE FRAME AFTER CONVERSION)
        if check_frames:
            for index, frame in enumerate(frames):
                # Construct a filename for each frame
                frame_filename = f"frame_{index:04d}.jpeg"
                frame_path = os.path.join(frames_directory_path, frame_filename)
                # Save the frame
                cv2.imwrite(frame_path, frame)

        out.release()

    @staticmethod
    def start_input_logging(recording_flag, input_filename, start_time, paused_flag, pause_start_time,
                            total_pause_duration):
        input_events = []

        def calculate_elapsed_time():
            now = time.time()
            current_pause_duration = now - pause_start_time.value if paused_flag.value else 0
            total_paused = total_pause_duration.value + current_pause_duration
            return round(now - start_time - total_paused, 2)

        def on_press(key):
            if not paused_flag.value:  # Log keys only when not paused
                elapsed_time = calculate_elapsed_time()
                input_value = getattr(key, 'char', str(key))
                input_events.append(
                    {"input_type": "keyboard", "input_value": input_value, "elapsed_time": elapsed_time})

        def on_click(x, y, button, pressed):
            if pressed and not paused_flag.value:  # Log mouse clicks only when not paused
                elapsed_time = calculate_elapsed_time()
                button_name = str(button).split('.')[1]
                input_events.append({"input_type": "mouse", "input_value": f"{button_name} at ({x}, {y})",
                                     "elapsed_time": elapsed_time})

        # Start listeners in non-blocking mode
        keyboard_listener = KeyboardListener(on_press=on_press)
        mouse_listener = MouseListener(on_click=on_click)
        keyboard_listener.start()
        mouse_listener.start()

        try:
            while recording_flag.value:
                time.sleep(0.1)  # Short sleep to reduce CPU usage
        finally:
            keyboard_listener.stop()
            mouse_listener.stop()
            keyboard_listener.join()
            mouse_listener.join()

            # Ensure the data is saved when the recording stops
            df = pd.DataFrame(input_events)
            df.to_csv(input_filename, index=False)

    def open_recording(self):
        current_working_directory = os.getcwd()
        filename = filedialog.askopenfilename(initialdir=f"{current_working_directory}/data", title="Select file", filetypes=(("AVI files", "*.avi"), ("all files", "*.*")))
        if filename:
            try:
                os.startfile(filename)
                logging.info(f"INFO:Opened recording: {filename}")
            except Exception as e:
                messagebox.showerror("Error", "Failed to open the file.")
                self.logger.log(f"Error:Failed to open recording: {filename}. Error: {e}")
