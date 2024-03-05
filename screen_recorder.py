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
import pyaudio
import wave

from custom_button import CustomButton, ModernButton
from custom_logger import CustomLogger


class ScreenRecorder:
    def __init__(self, root):
        self.audio_flag = None
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
        self.audio_recording_process = None
        self.start_time = None
        self.frames = []
        self.audio_device_index = None

        self.record_inputs = True
        self.record_video = True
        self.record_frames = True

        self.record_inputs_option = None
        self.record_video_option = None
        self.record_frames_option = None

        self.custom_font = tkFont.Font(family="Helvetica", size=10, weight="bold")
        self.record_inputs_option_label = None
        self.record_video_option_label = None
        self.record_frames_option_label = None

        self.logger = CustomLogger()
        self.logger.log("INFO:Logger has been initialized.")
        # self.logger.save()  # Explicitly call save if you want to close the log file immediately
        
        # Shared values to control recording and pause across processes
        self.recording_flag = Value(ctypes.c_bool, False)
        self.audio_flag = Value(ctypes.c_bool, False)
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
        self.root.geometry("1000x600")
        self.root.configure(background="#141414")

        # Define the layout grid
        # self.root.rowconfigure(0, weight=1)
        # self.root.rowconfigure(1, weight=1)
        # self.root.rowconfigure(2, weight=1)
        # self.root.rowconfigure(3, weight=1)
        #
        # self.root.columnconfigure(0, weight=2)
        # self.root.columnconfigure(1, weight=4)
        # self.root.columnconfigure(2, weight=4)

        # Configure the main window's columns and rows
        self.root.columnconfigure(0, weight=1)  # Pane column takes up 20% of the width
        self.root.columnconfigure(1, weight=9)  # Remaining space
        self.root.rowconfigure(0, weight=1)  # Only one row that takes up all the height

        # Left column setup begins
        self.button_frame = tk.Frame(self.root, bg="green")
        self.button_frame.grid(row=0, column=0, sticky="nsew")
        self.button_frame.columnconfigure(0, weight=1)

        # Configure the button pane's rows to distribute space among buttons
        # Assuming 4 buttons for example, adjust as needed
        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.rowconfigure(1, weight=8)
        self.button_frame.rowconfigure(2, weight=1)

        self.button_frame_top = tk.Frame(self.button_frame, bg="#000000")
        self.button_frame_top.grid(row=0, column=0, sticky="nsew")
        self.button_frame_top.rowconfigure(0, weight=5)
        self.button_frame_top.rowconfigure(1, weight=5)
        self.button_frame_top.columnconfigure(0, weight=5)
        self.button_frame_top.columnconfigure(1, weight=5)

        self.button_frame_middle = tk.Frame(self.button_frame, bg="#000000")
        self.button_frame_middle.grid(row=1, sticky="nsew")
        self.button_frame_bottom = tk.Frame(self.button_frame, bg="#000000")
        self.button_frame_bottom.grid(row=2, sticky="nsew")

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
        for i in range(10):
            self.button_frame_middle.rowconfigure(i, weight=i)

        self.button_frame_middle.columnconfigure(0, weight=1)


        self.fps_label = tk.Label(self.button_frame_middle, text="FPS:", bg="#141414", fg="white",
                                  font=self.custom_font)
        self.fps_label.grid(row=1, column=0, padx=(5, 0), pady=0, sticky="ew")

        self.fps_option = ttk.Combobox(self.button_frame_middle, values=['5', '10', '15', '20', '24', '30', '60'], state="readonly")
        self.fps_option.grid(row=1, column=1, padx=(0, 5), pady=0, sticky="ew")
        self.fps_option.set(30)  # Default value

        # BUTTON FRAME BOTTOM SETUP
        self.button_frame_bottom.rowconfigure(0, weight=3)
        self.button_frame_bottom.rowconfigure(1, weight=3)
        self.button_frame_bottom.rowconfigure(2, weight=3)
        self.button_frame_bottom.columnconfigure(0, weight=9)
        self.button_frame_bottom.columnconfigure(1, weight=1)

        self.record_inputs_option = tk.Checkbutton(
            self.button_frame_bottom, text="", bg="#141414", fg="white", font=self.custom_font
        )
        self.record_inputs_option.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="nsew")
        self.record_video_option = tk.Checkbutton(
            self.button_frame_bottom, text="", bg="#141414", fg="white", font=self.custom_font
        )
        self.record_video_option.grid(row=1, column=1, padx=(0, 5), pady=5, sticky="nsew")
        self.record_frames_option = tk.Checkbutton(
            self.button_frame_bottom, text="", bg="#141414", fg="white", font=self.custom_font
        )
        self.record_frames_option.grid(row=2, column=1, padx=(0, 5), pady=5, sticky="nsew")


        self.record_inputs_option_label = tk.Label(
            self.button_frame_bottom, bg="#141414", fg="white",
            text="Capture User Inputs", font=self.custom_font
        )
        self.record_inputs_option_label.grid(row=0, column=0, padx=(5, 0), pady=5, sticky="nsew")
        self.record_video_option_label = tk.Label(
            self.button_frame_bottom, bg="#141414", fg="white",
            text="Capture Video Capture", font=self.custom_font
        )
        self.record_video_option_label.grid(row=1, column=0, padx=(5, 0), pady=5, sticky="nsew")
        self.record_frames_option_label = tk.Label(
            self.button_frame_bottom, bg="#141414", fg="white",
            text="Capture Video Frames", font=self.custom_font
        )
        self.record_frames_option_label.grid(row=2, column=0, padx=(5, 0), pady=5, sticky="nsew")
        # Left column setup ends

        self.audio_device_index = self.get_device_index_by_name()

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
            self.logger.log("INFO:Recording Started.")
            self.generate_file_paths()
            self.recording_flag.value = True
            self.audio_flag.value = True
            self.paused_flag.value = False
            self.start_time = time.time()
            self.start_background_processes()
            self.update_ui_state(started=True)

    def start_capturing_audio(self):
        # Only start capturing if not already doing so
        if self.audio_recording_process is None or not self.audio_recording_process.is_alive():
            # Flag to control audio recording, similar to video
            # self.audio_flag = Value(ctypes.c_bool, True)

            # Define the audio file name and path
            audio_filename = os.path.join(self.main_directory_path, 'audio.wav')

            # Initialize and start the audio recording process
            self.audio_recording_process = Process(target=self.capture_audio,
                                                   args=(audio_filename, self.audio_flag, self.recording_flag, self.audio_device_index))
            # while recording_flag_value and audio_flag_value:
            self.audio_recording_process.start()

    def start_background_processes(self):
        fps = int(self.fps_option.get())
        self.recording_process = Process(target=self.record, args=(self.filename, fps, self.recording_flag, self.paused_flag, self.frames_directory_path))
        self.input_logging_process = Process(target=self.start_input_logging, args=(
            self.recording_flag, self.input_filename, self.start_time, self.paused_flag, self.pause_start_time, self.total_pause_duration
        ))
        self.recording_process.start()
        self.start_capturing_audio()
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
            self.audio_flag.value = False
            if self.recording_process is not None:
                self.recording_process.join()
            if self.input_logging_process is not None:
                self.input_logging_process.join()
            if self.audio_recording_process is not None:
                self.audio_recording_process.join()

            # Paths to your audio and video files
            audio_filename = os.path.join(self.main_directory_path, 'audio.wav')  # Example path
            video_filename = self.filename  # Already defined in start_recording
            output_filename = os.path.join(self.main_directory_path, 'final_output.mp4')  # Desired output path

            # Call the merge function
            self.merge_audio_video(audio_filename, video_filename, output_filename)

            # UI update and cleanup logic here
            self.update_ui_state(started=False)
            self.logger.log(f"INFO:Merge complete. Output saved to {output_filename}")

            self.update_ui_state(started=False)

    @staticmethod
    def record(filename, fps, recording_flag, paused_flag, frames_directory_path):
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

    @staticmethod
    def capture_audio(audio_filename, audio_flag, recording_flag, device_index):
        chunk = 1024
        _format = pyaudio.paInt16
        channels = 2
        sample_rate = 44100
        p = pyaudio.PyAudio()
        stream = p.open(format=_format, channels=channels, rate=sample_rate, input=True, frames_per_buffer=chunk,
                        input_device_index=device_index)
        frames = []

        print("Audio Capture Loop Starting")
        while recording_flag.value and audio_flag.value:
            data = stream.read(chunk)
            frames.append(data)

        print("Looped Exited; Stoping and Closing stream")
        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(audio_filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(_format))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        print("Audio file saved")

    @staticmethod
    def merge_audio_video(audio_filename, video_filename, output_filename):
        command = [
            'C:/ProgramData/chocolatey/lib/ffmpeg/tools/ffmpeg/bin/ffmpeg.exe',
            '-i', video_filename,
            '-i', audio_filename,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            output_filename
        ]
        try:
            subprocess.run(command, check=True)
            print(f'Successfully merged into {output_filename}')
        except subprocess.CalledProcessError as e:
            print(f'Failed to merge audio and video: {e}')
            exit()

    def list_audio_devices(self):
        p = pyaudio.PyAudio()
        print("Available audio devices:")
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            print(f"{i}: {info.get('name')}")
        p.terminate()

    def select_audio_device(self):
        self.list_audio_devices()
        device_index = int(input("Select device index: "))  # Manually select the device based on printed list
        return device_index

    @staticmethod
    def get_device_index_by_name(target_name="What U Hear"):
        p = pyaudio.PyAudio()
        device_index = None
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if target_name in device_info['name']:
                device_index = i
                break
        p.terminate()
        return device_index
