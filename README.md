# ADB File Explorer `beta v0.4`

<pre>
Simple File explorer for ADB devices

Allows you to see list of files on your device
and upload to/download it
</pre>

<span style="color: yellow">
# TODO<br/>
# Project not finished and requires further development<br/>
# Possible future features:<br/>
# ● File: Settings - modify settings and store in <code>settings.json</code><br/>
# ● Tool: APK Manager - list/download apks <br/>
</span>

## Screenshots

* Devices screen <br/>
  ![Devices, screenshot](previews/devices.png)
* Files screen <br/>
  ![Files, screenshot](previews/files.png)

<pre>*Window frame style depends on OS type and theme</pre>

## Contains [Main packages]

/res - project resources <br/>
/src - project source code in `python` <br/>
adb should exist in project root folder or in `PATH` variable

### Requirements

* `Python 3.8` or `Python 3.9`
  (other versions not tested)

* virtual environment (Optional)

* pip installation with `requirements.txt`

## What works

<b>At the moment works features like:</b>

* Showing devices
* Connecting to devices by IP / Disconnecting
* Showing files and directories of devices
* Pulling files
* Pushing files

# Todo 2
<span style="color: red">
<h2>Not works:</h2>
- Copying files <br/>
- Moving files <br/>
- Deleting files <br/>
- Renaming files <br/>
in the device
</span>

## Introduction to the code

<pre>
# TODO("Write brief description")
</pre>


## DEV: NEW FEATURES

* Notification center (finished / may have some changes)
* `python-adb` (finished / may have some changes)
* Threading all tasks (not finished)