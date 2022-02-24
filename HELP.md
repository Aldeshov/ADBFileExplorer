### Installation (Linux)

```shell
# Here project root path is `~/ADBFileExplorer`

# Install required packages
sudo apt update && sudo apt upgrade
sudo apt install swig openssl libssl-dev gcc make perl python3-dev

# Install python environment
cd ~/ADBFileExplorer # Root folder of the project
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Running Application
source venv/bin/activate
cd ~/ADBFileExplorer # Root folder of the project
python src/app.py

# Adb core settings in src/core/daemons.py

...
class Adb:
...
    __instance__ = instances[COMMON_ANDROID_ADB]  # Change array index
...

# COMMON_ANDROID_ADB - to use external `adb` tool
# PYTHON_ADB - to use `python-adb` libs 
```

### Installation (Windows)

Coming soon
