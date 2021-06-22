from timtai.util import replace_img
from aiohttp import ClientSession, web
import cv2
import numpy as np
import base64
from os import environ
import validators


@web.middleware
async def error_handler(request, handler):
    try:
        response = await handler(request)
        if response.status == 200 or response.status == 201:
            return response
        message = response.message
    except web.HTTPException as ex:
        status = ex.status_code
        message = ex.reason
        return web.Response(
            text=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Timtai</title>
        <meta name="og:title" content="Timtai">
    </head>
    <body>
        <h1>Error Code {status}</h1>
        <p>{message or "An error occurred."}</p>
    </body>
    </html>
        """,
            content_type="text/html",
            status=status or 500,
        )


async def handle(request: web.Request):
    url = request.query.get("image")
    print(url)
    if not url or validators.url(url) is not True:
        raise web.HTTPBadRequest(reason="Invalid image url.")
    data = bytearray()

    async with ClientSession() as session:
        async with session.get(url) as resp:
            while not resp.content.at_eof():
                chunk = await resp.read()
                if not chunk:
                    break
                data += chunk
    # convert string of image data to uint8
    nparr = np.frombuffer(data, np.uint8)

    # decode image
    img: np.ndarray = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

    # Load the cascade
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    # Detect faces
    faces = face_cascade.detectMultiScale(img, 1.1, 4)
    tim_img: np.ndarray = cv2.imread("tim.png")

    for f in faces:
        tim_1: np.ndarray = tim_img.copy()
        replace_img(img, tim_1, (f[0], f[1], f[2], f[3]))
        # cv2.imshow("image", img)
        # cv2.waitKey()
        # raise web.HTTPInternalServerError(
        #     reason=f"Could not create image with dimensions {tim_1.shape}"
        # )
    encoded = base64.b64encode(cv2.imencode(".jpg", img)[1]).decode()

    return web.Response(
        text=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Timtai</title>
        <meta name="og:image" content="data:image/jpeg;base64, {encoded}">
        <meta name="og:title" content="Timtai">
    </head>
    <body>
        <img src="data:image/jpeg;base64, {encoded}">
    </body>
    </html>
    """,
        content_type="text/html",
    )


app = web.Application(middlewares=[error_handler])
app.add_routes([web.get("/", handle)])

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(environ.get("PORT") or "8080"))
