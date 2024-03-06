# Desktop Recorder

Desktop Recorder is a Python-based application designed to record desktop screens, including mouse and keyboard inputs. It saves each recording in a directory named after the datetime it was created, under a `data` folder. This tool is particularly useful for creating datasets for neural network training, testing, and validation, making it an invaluable resource for developers and researchers working in machine learning, AI development, or data science.

## Features

- **Screen Recording**: Captures your desktop screen as a video in AVI format, which can be used as visual data for neural network training.
- **Input Logging**: Records all keyboard and mouse inputs during the recording session in a CSV file, providing additional data points for model training.
- **Frame Storage**: Saves individual frames of the video in JPEG format in a separate directory, allowing for frame-by-frame analysis or training on static images.
- **Customizable UI**: Comes with a simple yet effective user interface to control the recording process, making data collection as straightforward as possible.

## Installation

To use Desktop Recorder, ensure Python is installed on your system. Follow these steps to set up the application:

1. Clone the repository to your local machine:
   ```
   git clone https://github.com/lee-cha-dev/desktop-recorder.git
   ```
2. Navigate to the cloned directory:
   ```
   cd desktop-recorder
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To start the application, run the following command in the terminal:

```
python main.py
```

The application window will open, providing you with options to start, pause, stop, and open recordings. You can also configure the recording settings such as FPS and whether to capture video, frames, and inputs.

## Technologies

- **Python**: The core programming language used for development.
- **Tkinter**: For creating the application's graphical user interface.
- **OpenCV (cv2)**: For capturing and processing video frames.
- **PyAutoGUI**: For capturing screenshots.
- **Pynput**: For logging keyboard and mouse inputs.
- **Pandas**: For storing input logs in a CSV format.

## Purpose

The Desktop Recorder was specifically developed to facilitate the creation of datasets for neural network models. By capturing detailed video recordings in AVI format, frames in JPEG format, and user inputs in CSV format, it provides a rich source of data that can be used for training, testing, and validating machine learning models. This makes it an essential tool for anyone involved in AI development, offering a practical solution for data collection and preprocessing.
