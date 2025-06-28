This Python script return the latest earthquake info. in Japan. This info. is taken from the RSS feed from JMA (気象庁).
I wrote this to let my Home Assistant speak an earthquake info.
## How to install this for Home Assistant
Assuming this script is saved as `www/shell_command/jma-earthquake.py`,
put the following YAML code in your `configuration.yaml` file
```jma-earthquake.py
command_line:
  - sensor:
      name: Latest Earthquake
      command: "python3 www/shell_command/jma-earthquake.py"
      scan_interval: 300
```
In this case, the earthquake info is obtained every 5 minutes. Do not forget ```chmod +x jma-earthquake.py```.

*JMA limits the total size of downloading data up to 10GB per day. Roughly, 100KB of data is downloaded once this script is called.*

The `MAGNITUDE_THRESHOLD` value determins if the latest earthquake is big enough to report or not. You may change its value according to your needs.
