from setuptools import setup

APP = ['pomodoro.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
        #'PyRuntimeLocations': [
        #        '@executable_path/../Frameworks/libpython3.7.dylib',
        #        '/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.7/lib/libpython3.7.dylib'
        #       ]
    },
    'packages': ['rumps'], #, 'pickle', 'math', 'googleapiclient', 'google_auth_oauthlib', 'google', 'datetime'
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

#python setup.py py2app