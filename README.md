# KeyCounter

How many keys do you press each day?

# Requirements

On Windows:

```
pywin32
pyHook
```

On macOS:

```
pyObjc
```

Universal (non platform-related) requirements are gathered into `requirements.txt`.

To build from source code, you'll need `pyinstaller` as well.

# How to build

Run `pyinstaller --clean --noconfirm counter.spec`.

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
