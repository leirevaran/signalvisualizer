import PyInstaller.__main__
# from PyInstaller.utils.hooks import collect_data_files

# subprocess.check_call([sys.executable, "-m", "pip", "install", "librosa"])

PyInstaller.__main__.run([
    'signalvisualizer.py',
    '--onefile',
    '-w',
    '--icon=./images/icon.ico'
])