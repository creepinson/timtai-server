from aiohttp import web
import cv2
import numpy as np
import aiohttp
import asyncio
import base64
from os import environ


async def handle(request: web.Request):
    url = request.query.get("image")
    data = bytearray()

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            while not resp.content.at_eof():
                chunk = await resp.read()
                if not chunk:
                    break
                data += chunk
    # convert string of image data to uint8
    nparr = np.frombuffer(data, np.uint8)

    # decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

    # Load the cascade
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    # Detect faces
    faces = face_cascade.detectMultiScale(img, 1.1, 4)
    tim_img = cv2.imread("tim.png")

    for (x, y, w, h) in faces:
        tim_1 = tim_img.copy()
        new_size = (w, h)
        tim_1 = cv2.resize(tim_1, new_size)
        img[y : y + tim_1.shape[0], x : x + tim_1.shape[1]] = tim_1

    encoded = base64.b64encode(cv2.imencode(".jpg", img)[1]).decode()

    return web.Response(
        text=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
        <meta name="og:image" content="data:image/jpeg;base64, {encoded}">
    </head>
    <body>
        <img src="data:image/jpeg;base64, {encoded}">
    </body>
    </html>
    """,
        content_type="text/html",
    )


app = web.Application()
app.add_routes([web.get("/", handle)])

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(environ.get("PORT") or "8080"))
