#!/usr/bin/env python3
import rumps
import requests
import os
import json
import webbrowser
import AppKit

class AmbientTempApp(rumps.App):
    def __init__(self, cfg):
        self.temperature = 0.0
        self.last_data = {}
        self._active_windows = []

        super(AmbientTempApp, self).__init__(f"{self.temperature}°F")
        self.menu_base = [
            rumps.MenuItem("Open Ambient Weather", self.open_ambient_weather),
            rumps.MenuItem("Show Info", self.show_info),
            rumps.MenuItem("Quit", rumps.quit_application)
        ]

        self.cfg = cfg
        self.api_key = cfg.get('api_key')
        self.application_key = cfg.get('application_key')
        self.timer = rumps.Timer(self.update_temp, cfg.get('update_seconds', 60))  # Update every 60 seconds
        self.timer.start()

    @rumps.clicked("Open Ambient Weather")
    def open_ambient_weather(self, _):
        """
        Opens the Ambient Weather website in the default web browser.
        """
        webbrowser.open("https://ambientweather.net/dashboard")

    def show_scrollable_text_window(self, title, text):
        # Create window
        window = AppKit.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            ((0.0, 0.0), (500.0, 400.0)),  # position and size
            AppKit.NSTitledWindowMask | AppKit.NSClosableWindowMask | AppKit.NSResizableWindowMask,
            AppKit.NSBackingStoreBuffered,
            False
        )
        window.setTitle_(title)

        # Create scroll view
        scroll_view = AppKit.NSScrollView.alloc().initWithFrame_(((0, 0), (500, 400)))
        scroll_view.setHasVerticalScroller_(True)
        scroll_view.setHasHorizontalScroller_(False)
        scroll_view.setAutohidesScrollers_(True)

        # Create text view
        text_view = AppKit.NSTextView.alloc().initWithFrame_(((0, 0), (480, 1000)))
        text_view.setEditable_(False)
        text_view.setString_(text)
        text_view.setVerticallyResizable_(True)
        text_view.setHorizontallyResizable_(False)
        text_view.setAutoresizingMask_(AppKit.NSViewWidthSizable)

        # Embed text view in scroll view
        scroll_view.setDocumentView_(text_view)
        window.setContentView_(scroll_view)

        # Show the window
        window.makeKeyAndOrderFront_(None)

        # Prevent premature garbage collection
        self._active_windows.append(window)

        # Remove from active list when window closes
        class WindowDelegate(AppKit.NSObject):
            def windowWillClose_(self, notification):
                if window in self._active_windows:
                    self._active_windows.remove(window)

        delegate = WindowDelegate.alloc().init()
        window.setDelegate_(delegate)

    @rumps.clicked("Show Info")
    def show_info(self, _):
        lines = [f"{k}: {v}" for k, v in self.latest_data.items()]
        message = "\n".join(lines)
        self.window = self.show_scrollable_text_window("Ambient Weather Data", message)

    def do_nothing(self, _):
        pass

    def update_temp(self, _):
        """
        Fetches the current temperature and updates the menu item.
        """
        self.get_ambient_temperature()
        print(f"Current temperature: {self.temperature}°F")
        self.title = f"{self.temperature}°F"
        extra_menu = [ None ]
        for sensor in self.cfg.get('sensors', []):
            sensor_name = sensor.get('name', 'Unknown Sensor')
            sensor_key = sensor.get('key', 'N/A')
            sensor_val = self.latest_data.get(sensor_key, 'N/A')
            sensor_unit = sensor.get('unit', '°F')
            if sensor_val != 'N/A':
                extra_menu.append(rumps.MenuItem(f"{sensor_name}: {sensor_val}{sensor_unit}", self.do_nothing))

        self.menu.clear()
        self.menu = self.menu_base + extra_menu


    def get_ambient_temperature(self):
        """
        Fetches the current temperature from the user's Ambient Weather station.

        Args:
            api_key (str): Your Ambient Weather API Key.
            application_key (str): Your Ambient Weather Application Key.

        Returns:
            float: The current temperature in Fahrenheit, or None if an error occurs.
        """
        url = "https://api.ambientweather.net/v1/devices"
        params = {
            "apiKey": self.api_key,
            "applicationKey": self.application_key
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            devices = response.json()

            if not devices:
                print("No devices found.")
                return None

            # Assuming the first device is the one you're interested in
            self.latest_data = devices[0].get('lastData', {})
            self.temperature = self.latest_data.get('tempf')

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")


if __name__ == "__main__":
    config_path = os.path.expanduser("~/.ambient_config.json")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            api_key = config.get('api_key')
            application_key = config.get('application_key')
            update_seconds = config.get('update_seconds', 60)
            AmbientTempApp(config).run()
    except Exception as e:
        print(f"Error loading config: {e}")
        exit(1)