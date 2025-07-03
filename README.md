This Python scripts return the latest weather and earthquake info. from JMA (気象庁).

## jma-earthquake.py
I wrote this to let my Home Assistant speak an earthquake info.

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

## JMA-Weather-Chart.py
This script is to obtain the latest weather chart (天気図) from JMA (気象庁). This script is designed
reduce the traffic to JMA. Note that the weather data are collected every 3 hours (0, 3, 6, 9, 12, 15, 18, 21),
and it takes 2:10 to produce a weather cahrt ([reference](https://www.jma.go.jp/jma/kishou/know/kurashi/tenkizu.html)).

Here is my configuration, assuming this script is copied as `www/shell_command/JMA-Weather-Chart.py`

```JMA-Weather-Chart.py
command_line:
  - sensor:
      name: Latest Weather Chart
      command: "python3 www/shell_command/JMA-Weather-Chart.py"
      scan_interval: 1800
```

To display the chart, I use [Refreshable Picture Card](https://github.com/dimagoltsman/refreshable-picture-card).
