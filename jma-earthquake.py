import requests
import xml.etree.ElementTree as ET
import datetime

# XML フィードURL
FEED_URL = "https://www.data.jma.go.jp/developer/xml/feed/eqvol.xml"

ATOM = "{http://www.w3.org/2005/Atom}"
SEISMOLOGY1 = "{http://xml.kishou.go.jp/jmaxml1/body/seismology1/}"
ELEMENTBASIS1 = "{http://xml.kishou.go.jp/jmaxml1/elementBasis1/}"

MAGNITUDE_THRESHOLD = 4.0

OUTPUT_FILE = "jma_earthquake.txt"  # HAのwwwフォルダ（内部でアクセス可能）

def fetch_latest_earthquake():
    res = requests.get(FEED_URL)
    res.raise_for_status()
    rt = ET.fromstring(res.content)
    for entry in rt:
        if( entry.tag == ATOM+"entry" ):
            title = entry.find( ATOM+"title" ).text
            if( title == "震源・震度に関する情報" ):
                link = entry.find(ATOM+'id').text
                eq = requests.get(link)
                eq.raise_for_status()
                ert = ET.fromstring(eq.content)

                body = ert.find(SEISMOLOGY1+'Body')
                quake = body.find(SEISMOLOGY1+'Earthquake')
                time = quake.find(SEISMOLOGY1+'OriginTime').text
                hypo = quake.find(SEISMOLOGY1+'Hypocenter')
                area = hypo.find(SEISMOLOGY1+'Area')
                area_name = area.find(SEISMOLOGY1+'Name').text
                coord = area.find(ELEMENTBASIS1+'Coordinate').text
                magstr = quake.find(ELEMENTBASIS1+'Magnitude').text

                if( float(magstr) > MAGNITUDE_THRESHOLD ):
                    dt = datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S%z")
                    th = dt.strftime( "%H" )
                    tm = dt.strftime( "%M" )
                    coordlist = coord.split( "-" )
                    depth = str( int(float(coordlist[1][:-1])/1000) )
                    
                    output = f"{th}時{tm}分頃、{area_name}の深さ{depth}キロでマグニチュード{magstr}の地震がありました。"
                    
                    print( output )
                    break

if __name__ == "__main__":
    fetch_latest_earthquake()
