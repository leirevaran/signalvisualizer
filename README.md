# Signal Visualizer: introducing singal processing concepts into musical education

## Description

Signal Visualizer is an application for musical education. It aims to show which are the most used frequency analysis techniques in a visual and interactive way. This application allows the following functions:

* Generation of signals.
* Imports of sounds.
* Recordings of new sounds.
* Visualization of frequency analysis techniques.

It also contains user assistance and customization of the application.

The following image shows an schema of the architecture of the application:

<img src="icons/architecture.jpeg" alt="architecture" width="400"/>

As depicted in the figure, the solution comprises a set of subsidiary modules that depend on a main module. Based on their functionality, the modules are classified into the following types:

* **Main module**: The primary interface of the application. It provides access to other modules.
* **Generation modules**: These modules create a selection of synthetic sound signals for loading into the control menu window.
* **Input modules**: They serve to load real audio into the control menu window, whether audio files or recordings made in real-time.
* **Control menu module**: It allows to configure the parameters of different frequency analysis techniques and visualize the results.
* **Help module**: It displays user assistance for each module.
* **Configuration module**: It enables customization of the color of the spectrogram.

The main module is positioned at the center of the diagram and is responsible for executing the other modules, as represented by arrows originating from it. When the user generates an audio signal via generation or input modules, they can always load it into the control menu window to analyze it. The help module is accessible from any generation and import module, as well as from the control menu module.

### GENERATION MODULES

The software can generate the following signals: pure tone, free addition of pure tones, square wave, sawtooth wave, and three types of noise. These modules have the objective of generating synthetic signals so the student can learn under which parameters they are calculated, and how the change of each parameter affects the resulting signal.

### INPUT MODULES

The input modules allow to load existing audio to the application and to record new sounds. The objective of these modules is to let the user choose the exact fragment they want to analyze by its frequency. There are two input modules: load and record.

### CONTROL MENU MODULE

The control menu module is the most important part of the application. The objective of this module is to teach students how frequency techniques work, the different elements involved in them, and how changing those elements affects the spectrum of the signal. It allows to toggle between different analysis techniques and to control the main configurable parameters for each technique. In this way, students learn to select the most suitable configuration to obtain the desired information. It focuses on eight different modes: the
Fourier Transform, the Short-Time Fourier Transform (which applies the Fourier transform to a windowed segment of the signal), the spectrogram, the short-time-energy, the pitch, the spectral centroid, and the filtering. Since the program allows opening multiple control
menu windows, it is possible to compare the results of the analyses performed over different signals and with different parameter values.

### HELP MODULE

Each generation and import module, as well as the control menu window, contains a button to open the help window, which is a crucial component of the application. It not only provides information on the usage of each module, but also offers didactic explanations about
the signal characteristics and the application of available frequency analysis techniques.

### CONFIGURATION MODULE

This module allows changing the colormap of the spectrogram. The user can choose between seven groups of colormaps: Perceptually Uniform Sequential, Sequential, Sequential (2), Diverging, Cyclic, Qualitative, and Miscellaneous. In total, the user can choose between
83 colormaps to visualize the spectrogram. Once they save a color, all the spectrograms created afterwards will follow that colormap.

## Installation

Execute the file **setup.py** to obtain an executable of Signal Visualizer.

```bash
python setup.py
```
Then an executable called **signalvisualizer.exe** will be created into the **build** folder. Put the executable and the **csv**, **html**, **icons**, **library**, and **wav** folders in a separated folder. Now the executable should work.

## Usage

To run the application from a terminal, after installing all the requirements in **requirements.txt** use:

```bash
python signalvisualizer.py
```

## Authors and acknowledgment

This application has been developed by Leire Varela Aranguren under the supervision of Inma Hernáez Rioja.


