from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import requests
import json
import base64
from bs4 import BeautifulSoup
import re

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def download_link():
    URL = "https://voe.sx/egrivmdavdhn"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }
    
    html_page = requests.get(URL, headers=headers)
    if html_page.status_code != 200:
        raise HTTPException(status_code=404, detail="URL not accessible")
    
    soup = BeautifulSoup(html_page.content, 'html.parser')

    name_find = soup.find("title").text
    slice_start = name_find.index("Watch ") + 6
    name = name_find[slice_start:]
    slice_end = name.index(" - VOE")
    name = name[:slice_end]
    name = name.replace(" ","_")

    sources_find = soup.find_all(string=re.compile("var sources"))
    if not sources_find:
        raise HTTPException(status_code=404, detail="Sources not found")

    sources_find = str(sources_find)
    slice_start = sources_find.index("var sources")
    source = sources_find[slice_start:]
    slice_end = source.index(";")
    source = source[:slice_end]

    source = source.replace("var sources = ","")
    source = source.replace("\'","\"")
    source = source.replace("\\n","")
    source = source.replace("\\","")

    strToReplace = ","
    replacementStr = ""
    source = replacementStr.join(source.rsplit(strToReplace, 1))

    try:
        source_json = json.loads(source)
        link = base64.b64decode(source_json["mp4"]).decode('utf-8')
    except KeyError:
        try:
            link = base64.b64decode(source_json["hls"]).decode('utf-8')
        except KeyError:
            raise HTTPException(status_code=404, detail="Downloadable URL not found")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{name}</title>
    </head>
    <body>
        <h1>{name}</h1>
        <video width="800" controls>
            <source src="{link}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content, status_code=200)

# To run the app, use the command: uvicorn filename:app --reload
