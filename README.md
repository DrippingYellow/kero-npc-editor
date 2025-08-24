# kero-npc-editor
A sloppy editor for NPCs, Bullets, Particles, and more in the latest Windows versions of Kero Blaster. This could be improved with time, but it might be a while until I feel like putting in the time to update it... unless someone else wants to work on this.

# Pre-requisites
Requires the latest version of Python, as well as the Python modules bitstring and wxPython.

# How to use
1. Open `main.py` with Python.
2. Select `File>Open`, and choose a Kero Blaster v1.5.0.1 executable file (older versions not guaranteed to work due to differing NPC amounts).
3. Once the desired changes are made, select `File>Save` to save your progress to the .exe file. Note that despite taking you to the file browser, it does _not_ support saving changes to a new file in this state. You have to override an existing Kero Blaster executable.

Note: the Coin selection supports custom values (by replacing the text field with your desired number), but requires you to press Enter/Return in order to properly process it, otherwise it will revert upon switching to another unit/tab.

# Features to be added
- Properly labeling the units from a list file.
- "Advanced" tab option that allows you to modify the code and string offsets (_if_ you know what you're doing).
- Display screen for the unit's graphics and hitboxes in real time.
- Visual Editor for editing the unit's graphics rects.
- "Help" page to provide info on what all these values do.
