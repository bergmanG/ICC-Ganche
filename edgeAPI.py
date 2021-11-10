import requests
import config
from PIL import Image
import dataset
import timer
import io


def sendImg(ts):
    try:
        timer.stop()
        im = Image.open(dataset.getDir(ts)+str(ts)+'.png')
        im = im.resize((512, 512))
        imgByteArr = io.BytesIO()
        im.save(imgByteArr, format='PNG')
        imgByteArr = imgByteArr.getvalue()
        timer.start()
        files = {"media": imgByteArr}
        r = requests.post(config.URL_CLOUD+'/recognize', files=files)
        r = r.json()
        return int(r['ts'])

    except Exception as err:
        print(f"Error at sendImg: {err.args}")
