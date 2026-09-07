import urllib.request
import urllib.error
import os
import sys
from datetime import timedelta, datetime, timezone


JMA_WEATHERMAP_PREFIX = 'https://www.data.jma.go.jp/yoho/data/wxchart/quick'
IMAGE_TYPE = 'png'

PREFIX_DIR = 'www/shell_command'
FILENAME = 'JMA_WEATHER_CHART-latest'

# 古い天気図を残す日数
KEEP_DAYS = 2


def create_weather_chart_url():
    # JMAの天気図は観測時刻から約2時間10分後に公開される。
    # 余裕を見て2時間30分前の観測時刻を対象にする。
    dt = datetime.now(timezone.utc) - timedelta(hours=2.5)

    # 観測時刻は3時間間隔。
    hour = (dt.hour // 3) * 3

    return (
        f'{JMA_WEATHERMAP_PREFIX}/'
        f'{dt.year}{dt.month:02d}/'
        f'SPAS_COLOR_{dt.year}{dt.month:02d}{dt.day:02d}'
        f'{hour:02d}00.{IMAGE_TYPE}'
    )


def download_file(url, dst_path):
    try:
        with urllib.request.urlopen(url, timeout=30) as remote_file:
            with open(dst_path, 'wb') as local_file:
                local_file.write(remote_file.read())

        return True

    except urllib.error.HTTPError as e:
        # まだJMAで公開されていない場合。
        if e.code == 404:
            return False
        raise

    except urllib.error.URLError:
        # ネットワークエラーの場合も、
        # 既存のlatestはそのまま残す。
        return False


def cleanup_old_charts(prefix):
    """
    KEEP_DAYSより古い天気図を削除する。

    対象は SPAS_COLOR_*.png のみ。
    JMA_WEATHER_CHART-latest.png は削除しない。
    """

    cutoff = datetime.now(timezone.utc) - timedelta(days=KEEP_DAYS)

    for name in os.listdir(prefix):

        if not name.startswith('SPAS_COLOR_'):
            continue

        if not name.endswith(f'.{IMAGE_TYPE}'):
            continue

        path = os.path.join(prefix, name)

        # ファイル名からJMAの観測時刻を取得。
        # 例:
        # SPAS_COLOR_202609030600.png
        try:
            timestamp = name[
                len('SPAS_COLOR_'):
                len('SPAS_COLOR_') + 12
            ]

            chart_time = datetime.strptime(
                timestamp,
                '%Y%m%d%H%M'
            ).replace(tzinfo=timezone.utc)

        except (ValueError, IndexError):
            # 想定外のファイル名は安全のため無視。
            continue

        if chart_time < cutoff:
            try:
                os.remove(path)
            except OSError:
                pass


def download_weather_chart(prefix):
    url = create_weather_chart_url()

    # JMA側のファイル名。
    base = os.path.basename(url)

    # 例:
    # SPAS_COLOR_202609030600.png
    localfile = os.path.join(prefix, base)

    latest_chart = os.path.join(
        prefix,
        f'{FILENAME}.{IMAGE_TYPE}'
    )

    # ------------------------------------------------------------
    # 1. 必要な天気図が既に存在するか確認
    # ------------------------------------------------------------

    if not os.path.exists(localfile):

        # 一時ファイル。
        tmpfile = localfile + '.tmp'

        try:
            # JMAへのアクセスはここだけ。
            if download_file(url, tmpfile):

                # 完全にダウンロードできてから正式な名前へ。
                os.replace(tmpfile, localfile)

                # ------------------------------------------------
                # 2. latest.pngをatomicに更新
                # ------------------------------------------------

                tmp_latest = latest_chart + '.tmp'

                try:
                    with open(localfile, 'rb') as src:
                        with open(tmp_latest, 'wb') as dst:
                            while True:
                                data = src.read(1024 * 1024)

                                if not data:
                                    break

                                dst.write(data)

                    # 完全に書き終わってから置換。
                    os.replace(tmp_latest, latest_chart)

                finally:
                    try:
                        os.remove(tmp_latest)
                    except FileNotFoundError:
                        pass

        finally:
            # ダウンロード失敗などでtmpが残った場合。
            try:
                os.remove(tmpfile)
            except FileNotFoundError:
                pass

    # ------------------------------------------------------------
    # 3. 古い天気図を削除
    # ------------------------------------------------------------

    cleanup_old_charts(prefix)

    # HA Picture Cardから利用するパス。
    print(f'/local/shell_command/{FILENAME}.{IMAGE_TYPE}')


if __name__ == '__main__':

    if len(sys.argv) > 1:
        prefix = sys.argv[1]
    else:
        prefix = PREFIX_DIR

    os.makedirs(prefix, exist_ok=True)

    download_weather_chart(prefix)
