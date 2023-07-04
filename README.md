# Python-3D-Model-Viewer
![image](https://github.com/hellboy01gr/Python-3D-Model-Viewer/assets/106314960/ae335dd6-a23e-4405-b561-8aa0bec1a74c)
---
## What does it do?
It just displays .obj models in the specified color.

## Why is it so broken?
I only made this to practice and learn a few things.

## Should I expect updates in the future?
Maybe, I am not sure yet but I already have some changes and new features I want to add.

## How do I build this?
### Clone the repository
```git clone https://github.com/hellboy01gr/Python-3D-Model-Viewer```

### Install Python 3
Download the latest version of Python 3 from [here](https://www.python.org/downloads/) if you don't have it already.

### Install the required libraries
    1. imgui
    2. pygame
    3. numpy
    4. PyWavefront
    5. PyOpenGL
    6. PyInstaller

### Build it
In the directory where main.py is located run this in a cmd window:

```
pyinstaller --onefile main.py
```

If the build was successful you should see a folder named "dist" in the root of the project. In it you should see the main.exe file

### We are not done yet!
Place the meshes folder, imgui.ini and icon.png inside the dist folder .

You can now run main.exe and the program should open.
