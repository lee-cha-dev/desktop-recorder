# Desktop Recorder
Desktop Recorder is a Python-based application designed to facilitate the generation of rich datasets for training advanced machine learning models, including time series models and Generative Adversarial Networks (GANs). This tool streamlines the process of collecting user input and screen activity data, serving as a vital resource for researchers and developers in the field of AI.

## Project Motivation
The inception of the Desktop Recorder project was driven by the imperative need to streamline the process of generating high-quality, structured datasets for the development and refinement of advanced machine learning algorithms. Specifically, the tool is designed to address the challenges in collecting and preparing data for:

- **Time Series Analysis**: By capturing sequential user interactions and screen activities, Desktop Recorder facilitates the creation of datasets that are ideal for training models focused on time series analysis. This includes predictive modeling and anomaly detection in temporal data, where understanding the sequence and timing of events is crucial.

- **Generative Modeling**: The detailed recording of on-screen activities provides a rich dataset for training Generative Adversarial Networks (GANs) and other generative models. These AI models can learn to simulate human-computer interactions, generate synthetic data that mimics user behavior, or create realistic scenarios for testing and development purposes.

This application serves as a critical resource for AI researchers and developers, enabling them to efficiently gather and utilize data that mirrors real-world user behavior and interactions. By offering a direct pathway to acquire this data, Desktop Recorder significantly reduces the barriers to innovation in machine learning, particularly in the domains of time series analysis and generative modeling.

## Features
- **Screen Recording**: Captures the user's primary screen upon user command, recording all on-screen activities in AVI format. The application is designed to record the primary screen only.
- **Input Logging**: Logs keyboard presses and mouse clicks, capturing the specific keys or buttons pressed along with the x, y coordinates of mouse clicks. Mouse movements are only logged if accompanied by a click.
- **Frame Storage**: Saves individual frames of the video in JPEG format in a separate directory, allowing for frame-by-frame analysis or training on static images.

## Installation and Compatibility
Desktop Recorder is developed and tested exclusively for Windows 10. It is not compatible with other operating systems.
1. Clone the repository to your local machine:
   ```
   git clone https://github.com/lee-cha-dev/desktop-recorder.git
   ```
2. Navigate to the cloned directory:
   ```
   cd desktop-recorder
   ```
3. Create a conda environment:
   ```
   conda create -n env-name python=3.10
   ```
4. Activate the environment:
   ```
   conda activate env-name
   ```
5. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
Desktop Recorder requires the user to manually start the recording process by pressing the "Start Recording" button. This design choice ensures that users have full control over the data collection period and the specific sessions they wish to capture.

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
The Desktop Recorder was specifically developed to facilitate the creation of datasets for neural network models. By capturing detailed video recordings in AVI format, frames in JPEG format, and user inputs in CSV format, it provides a rich source of data that can be used for training, testing, and validating machine learning models. This makes it an essential tool for anyone involved in AI development, offering a practical solution for data collection.

## Acknowledgements
I am the sole contributor to the Desktop Recorder project and would like to acknowledge the contributions of the open-source community. The libraries and dependencies utilized in this project reflect the collaborative spirit of open-source development, and I am grateful for the support that has made this tool possible.
