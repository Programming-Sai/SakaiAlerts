from setuptools import setup

APP = ['main.py']
DATA_FILES = ['Sakai.json', 'Sakai-Log.json', 'credentials.json', 'icon.png', 'background_notify.py']
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'icon.icns',  
    'packages': ['kivy', 'kivymd', 'plyer', 'selenium', 'schedule'],
    'includes': ['Scrape'],
    'plist': {
        'CFBundleName': 'SakaiAlerts',
        'CFBundleDisplayName': 'SakaiAlerts',
        'CFBundleIdentifier': 'com.sai.SakaiAlerts',  
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleIconFile': 'icon.icns', 
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
