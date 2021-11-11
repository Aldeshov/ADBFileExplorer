# ADB File Explorer `alpha v0.32`

<pre>
Simple File explorer for ADB devices
Allows you to see list of files on your device and 
upload to/download it
</pre>

<span style="color: yellow">
# TODO<br/>
# Project not finished and requires further development<br/>
# Works well on Linux (Tested on: Ubuntu 20.04)<br/>
# On windows 10 has some issues<br/>
</span>

### Downloading
<a href='https://github.com/Aldeshov/ADBFileExplorer/releases/tag/alpha-v0.32'>
Download for Linux and Windows<br/>
</a>

## Screenshots
* About program <br/>
![About, screenshot](previews/about.png)
* Devices screen <br/>
![Devices, screenshot](previews/devices.png)
* Files screen <br/>
![Files, screenshot](previews/files.png)

<pre>*Window style depends on OS type and theme</pre>
## Contains

/bin - executable adb files <br/>
/assets - icons storage <br/>
/src - source code written in `python` <br/>

### Requirements
* `Python 3.8` or `Python 3.9`
  (other versions not tested)

* virtual environment (Optional)
* pip installation with <b> requirements.txt </b>


## What works

At the moment works features like:

* showing devices
* Connecting to devices by IP
* showing files and directories of devices
* pulling files
* pushing files

<span style="color: red">
<h2>Not works:</h2>
- Copying files <br/>
- Moving files <br/>
- Deleting files <br/>
- Renaming files <br/>
in the device
</span>

## Inroduction to the code

<pre>
Project main packages are:
<b>GUI</b> and <b>SERVICES</b>
app starts from <i>app.py</i> file

Folder <b>GUI</b> contains <i>PyQt5</i> ui elements, widgets, window etc.
Folder <b>SERVICES</b> contains files that runs subprocesses and gets data from <i>ADB</i>, converts it to models

The most editable file is <i>drivers.py</i>
it tries to get data from adb command, and converts it to models
At the moment, this file needs to be checked for operability on various types of devices.
</pre>

<pre>
P.S. Further development depends on my free time
</pre>
