import urllib.request
import os
from datetime import timedelta, datetime, tzinfo, timezone

JMA_WEATHERMAP_PREFIX = 'https://www.data.jma.go.jp/yoho/data/wxchart/quick'
IMAGE_TYPE = 'png'              # pdf is also available
PREFIX_DIR = '.'                # directory prefix for storing weather chart image
FILENAME = 'JMA_WEATHER_CHART-latest'
LATEST_CHART = f'{PREFIX_DIR}/{FILENAME}.{IMAGE_TYPE}' # file name of stored chart

def download_file(url, dst_path):
    with urllib.request.urlopen(url) as remote_file:
        with open(dst_path, 'wb') as local_file:
            local_file.write(remote_file.read())

def create_weather_chart_url():
    td = timedelta(hours=2.5)   # chart is ready after collecting weather data. This takes 2h10m or so.
    dt = datetime.now(timezone.utc) - td # chart file name is based on UTC time
    year = dt.year
    month = dt.month
    day = dt.day
    hour = int(dt.hour/3) * 3   # weather data is collected every 3 hours
    return f'{JMA_WEATHERMAP_PREFIX}/{year}{month:02d}/SPAS_COLOR_{year}{month:02d}{day:02d}{hour:02d}00.{IMAGE_TYPE}'
    
def download_weather_chart():
    url = create_weather_chart_url()
    base = os.path.basename(url)
    localfile = f'{PREFIX_DIR}/{base}'

    if not os.path.exists(LATEST_CHART):
        download_file(url, LATEST_CHART)
    else:
        # the picture card does not accept sumbolic link
        # so the mtime is used to check if newer chart is available or not
        ctime = datetime.fromtimestamp(os.path.getmtime(LATEST_CHART))
        prevt = datetime.now() - timedelta(hours=3)
        if (ctime < prevt):        # possibly new data is available
            download_file(url, localfile)
            # we cannot call two or more number os systemcalls for updating chart
            # beacuse there can be a timing bug if we do so
            # this is the reason why firstly downloading the file and then rename it.
            os.rename(localfile, LATEST_CHART)
    print(f'/local/shell_command/{FILENAME}.{IMAGE_TYPE}')
    
if __name__ == "__main__":
    download_weather_chart()
