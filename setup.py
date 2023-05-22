import subprocess
import sys
import PyInstaller.__main__
# from PyInstaller.utils.hooks import collect_data_files

subprocess.check_call([sys.executable, "-m", "pip", "install", "librosa"])

PyInstaller.__main__.run([
    '-w',
    '--icon=./icons/icon.ico',
    '--collect-data',
    'librosa',
    '--add-data',
    'csv;csv',
    '--add-data',
    'html;html',
    '--collect-all',
    'tkinterweb',
    '--hidden-import=sklearn.utils._typedefs',
    '--hidden-import=sklearn.metrics._pairwise_distances_reduction._datasets_pair',
    '--hidden-import=sklearn.metrics._pairwise_distances_reduction._middle_term_computer',
    '--hidden-import=sklearn.utils._heap',
    '--hidden-import=sklearn.utils._sorting',
    '--hidden-import=sklearn.utils._vector_sentinel',
    '--hidden-import=sklearn.neighbors._partition_nodes',
    '--onefile',
    'signalvisualizer.py'
])