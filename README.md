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

On Windows there is another requirement you need to manually install, which is
`pywin32`.

# How to build

Run `python build.py`. This will produce:

- The EXE executable file `dist/KeyCounter.exe` on Windows.
- The DMG disk image file `dist/KeyCounter.dmg` on macOS.

# How to use

On Windows just launch the exe file. The number is displayed in a transparent
window on the right bottom of your main display (right above the taskbar), and
the window is dynamically resized when needed.

On macOS you'll need to manually add the `.app` bundle to `Accessibility` list.
To do so you should click on the `Apple menu`, and go to `System preferences` >
 `Security and privacy` > `Privacy` > `Accessibility`. Click the `+` button to
add the `.app` bundle to app list, and check the checkbox before the app name.
You'll need to re-launch KeyCounter after this.

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
