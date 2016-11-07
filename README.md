# KeyCounter

[![Build status](https://ci.appveyor.com/api/projects/status/la2d42vxji2h7pwx?svg=true)](https://ci.appveyor.com/project/JokerQyou/keycounter)
[![Build Status](https://travis-ci.org/Microcore/KeyCounter.svg?branch=master)](https://travis-ci.org/Microcore/KeyCounter)

How many keys do you press each day?

KeyCounter is a small GUI application that continuously counts your key press,
and automatically exports data into CSV file for your future use.

# Requirements

Requirements are packed into `requirements` folder. If you want to build form
source code, you'll need to install the requirements listed in
`dev-requirements.txt` too.

# How to build

Currently all releases and CI builds are built with Python 2.7.

Run `python build.py`. This will produce:

- The EXE executable file `dist/KeyCounter.exe` on Windows.
- The DMG disk image file `dist/KeyCounter.dmg` on macOS.

# How to use

- On Windows:

  Launch the `.exe` file directly. You can also set a startup entry for it so
you don't need to manually run it each time your system restarts. Please note
that some anti-virus software like Windows Defender will report KeyCounter as
`Trojan`, but it's completely safe. Either trust KeyCounter or build the
executable from source, it's up to you.

  The count number will be displayed in a transparent window on the right
bottom of your primary display. It will automatically adjust itself to stay
just above the taskbar.

- On macOS:

  Drag the `.app` bundle from the dmg image to anywhere you want, and right
click on it, select "Open". If the system prevents it from running, open
"System Preferences", go to "Security and privacy", check for KeyCounter in
"General" panel, click "Open" if the button is presented.

  Then quit KeyCounter, go to "Privacy" panel in the same page, and add
KeyCounter into the list of apps authorized to accessibility functionality.
Launch KeyCounter again and you're good to go.

Linux is currently not supported. Any contribution is welcome, though.

# Known issues

On Windows, key events in the following processes are not working properly,
which seems to be an issue of `pyHook`:

- Task manager
- Remote desktop

On macOS, the following key events are not working properly:

- Function keys (media keys will work, however)
- Caps lock key (count only increase once if you press it twice)

# Get real time data

KeyCounter will count your key press, save and export data:

- If you tell it to quit. (Save on quit)
- If you press a key and it's already another day. (Daily reset)
- If the system is shutting down or restarting.

However under some circumstances you might want to get real time data. KeyCounter
provides a lightweight socket API server for this purpose. You can launch it
with the `--port` option, and KeyCounter will bind and listen on that port. You
can communicate with it via `multiprocessing.connection.Client` in Python.

Some limitations will be applied:

- port must be an integer in range of `(1024, 65535]`

Available commands:

- `quit` to tell KeyCounter to quit
- Any other command will trigger KeyCounter to send back current count
- If KeyCounter does not understand your command (e.g. send via Unix `nc`
  program or whatever) the connection will be closed

An example:

```
# Launch KeyCounter like this:
# - Windows: KeyCounter.exe --port 23334
# - macOS: KeyCounter.app/Contents/MacOS/KeyCounter --port 23334

from multiprocessing.connection import Client

c = Client(('127.0.0.1', 23334))
c.send('')  # Any command will trigger the output
print c.recv()

c.send('quit')  # KeyCounter will quit
c.close()
```
