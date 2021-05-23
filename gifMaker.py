import os
import re
from typing import Any
from flask import Flask, app, request, after_this_request
from flask import json
from flask.helpers import send_file, send_from_directory
from flask.json import jsonify
from werkzeug.utils import ArgumentValidationError
from pytube import YouTube
from moviepy.editor import *

app = Flask(__name__)


@app.route("/getGif", methods=["POST"])
def getVideoDetails():
    if request.method == "POST":
        requestData = request.get_json()
        videoUrl = requestData["url"]
        result = checkIfURLIsValid(videoUrl)
        if "startTime" not in requestData or "endTime" not in requestData or requestData["startTime"] == None or requestData["endTime"] == None:
            return jsonify("Error. Start and End timestamps required"), 200
        if requestData["endTime"] - requestData["startTime"] > 10:
            return jsonify("Gif too long. Max duration should be 10s"), 400
        if result:
            try:
                downloadedFile = downloadVideo(videoUrl, requestData["fileName"])
                finalFile = cutVideo(
                    downloadedFile, requestData["startTime"], requestData["endTime"]
                )
                return send_file(finalFile), 200
            except Exception:
                return jsonify("Failure"), 400
        else:
            return jsonify("Invalid URL")
        
# @app.teardown_request
# def removeFiles(response):
#     print("Callback executed")
#     for files in os.listdir(os.getcwd()):
#         if files.endswith('.mp4') or files.endswith('.gif'):
#             os.remove(files)
        


@app.route("/getInfo", methods=["POST"])
def getDetails():

    if request.method == "POST":
        requestData = request.get_json()
        videoUrl = requestData["url"]
        result = checkIfURLIsValid(videoUrl)
        if result:
            yt = YouTube(videoUrl)
            return jsonify(yt.title), 200
        else:
            return jsonify("Invalid Video"), 400
    


def downloadVideo(videoUrl: str, fileName: str) -> str:

    print("Inside download")
    yt = YouTube(videoUrl)
    yt.streams.filter(progressive=True).get_lowest_resolution().download(
        filename=fileName
    )
    print(fileName + ".mp4")
    return fileName + ".mp4"


def checkIfURLIsValid(videoURL: str) -> bool:

    regExp = re.compile(
        "^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"
    )
    return bool(re.match(regExp, videoURL))


def cutVideo(fileName: str, startTimestamp: int, endTimeStamp: int):

    print("Before CutVideo")
    cutVideo = (
        VideoFileClip(fileName)
        .subclip(startTimestamp, endTimeStamp)
        .resize(0.30)
        .set_fps(10)
    )
    print("video cropped")
    fileName = fileName.split(".")[0]
    print("strip ", fileName)
    cutVideo.write_gif(fileName + ".gif")
    print("After cutVideo")
    return fileName + ".gif"


if __name__ == "__main__":
    app.run(debug=True)
