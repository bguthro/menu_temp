#!/usr/bin/env python3
import rumps
import requests
import os
import json

class AmbientTempApp(rumps.App):
    def __init__(self, api_key, application_key):
        self.temperature = 0.0
        self.last_data = {}

        super(AmbientTempApp, self).__init__(f"{self.temperature}°F")
        self.menu = ["Show Info"]

        self.api_key = api_key
        self.application_key = application_key
        self.timer = rumps.Timer(self.update_temp, 60)  # Update every 60 seconds
        self.timer.start()

    @rumps.clicked("Show Info")
    def show_info(self, _):
        lines = [f"{k}: {v}" for k, v in self.latest_data.items()]
        message = "\n".join(lines)
        rumps.alert("Info", message)

    def update_temp(self, _):
        """
        Fetches the current temperature and updates the menu item.
        """
        self.get_ambient_temperature()
        print(f"Current temperature: {self.temperature}°F")
        self.title = f"{self.temperature}°F"


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
        with open(config_path, 'r') as f:
            config = json.load(f)
            api_key = config.get('api_key')
            application_key = config.get('application_key')
    except Exception as e:
        print(f"Error loading config: {e}")
        exit(1)

    AmbientTempApp(api_key,application_key).run()