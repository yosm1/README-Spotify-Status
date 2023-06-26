from flask import Flask, Response, render_template
from base64 import b64encode
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

import requests, json, os, random, time

SPOTIFY_URL_REFRESH_TOKEN = "https://accounts.spotify.com/api/token"
SPOTIFY_URL_NOW_PLAYING = "https://api.spotify.com/v1/me/player/currently-playing"
SPOTIFY_URL_RECENTLY_PLAY = "https://api.spotify.com/v1/me/player/recently-played?limit=10"

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_SECRET_ID = os.getenv("SPOTIFY_SECRET_ID")
SPOTIFY_REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")
SPOTIFY_BAR_COLOR = os.getenv("SPOTIFY_BAR_COLOR")
SPOTIFY_BADGE_COLOR = os.getenv("SPOTIFY_BADGE_COLOR")


app = Flask(__name__, template_folder="components")

access_token_cache = {
    "access_token": "",
    "refresh_ms": 1800,
    "last_update_time": 0
}


def getAuth():
    return b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_SECRET_ID}".encode()).decode("ascii")


def refreshToken():
    if time.time() < access_token_cache["refresh_ms"] + access_token_cache["last_update_time"]:
        return access_token_cache["access_token"]
    data = {
        "grant_type": "refresh_token",
        "refresh_token": SPOTIFY_REFRESH_TOKEN,
    }

    headers = {"Authorization": "Basic {}".format(getAuth())}

    response = requests.post(SPOTIFY_URL_REFRESH_TOKEN, data=data, headers=headers)
    access_token_cache["access_token"] = response.json()["access_token"]
    access_token_cache["last_update_time"] = time.time()
    return access_token_cache["access_token"]


def recentlyPlayed():
    token = refreshToken()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(SPOTIFY_URL_RECENTLY_PLAY, headers=headers)

    if response.status_code == 204:
        return {}

    return response.json()


def nowPlaying():
    token = refreshToken()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(SPOTIFY_URL_NOW_PLAYING, headers=headers)

    if response.status_code == 204:
        return {}

    return response.json()


def soundVisualizer(soundBars):
    soundVisualizerCSS = ""
    START_BAR = 1700  # default: 1700
    ANIMATIONS = ['animation1', 'animation2', 'animation3']
    for NTH in range(1, soundBars + 1):
        START_BAR += 100
        z = random.randint(0, 2)
        soundVisualizerCSS += ".spectrograph__bar:nth-child({0}) {{-webkit-animation-name: {1};animation-name: {1};" \
                              "-webkit-animation-duration: {2}ms;animation-duration: {3}ms;}}".format(NTH,
                                                                                                      ANIMATIONS[z],
                                                                                                      str(START_BAR),
                                                                                                      str(START_BAR))
    return soundVisualizerCSS


def loadImageB64(url):
    response = requests.get(url)
    return b64encode(response.content).decode("ascii")


def convertMsToMin(ms):
    seconds = int((ms / 1000) % 60)
    minutes = int((ms / (1000 * 60)) % 60)
    return str("%d:%d" % (minutes, seconds))


def spectrographWidth():
    return 98


def getSpotifyBadgeColor():
    default = "#1DB954"
    if SPOTIFY_BADGE_COLOR:
        return SPOTIFY_BADGE_COLOR
    return default


def setSpotifyObject(data):
    soundBars = 41
    soundVisualizerBar = "".join(["<div class='spectrograph__bar'></div>" for i in range(soundBars)])
    soundVisualizerCSS = soundVisualizer(soundBars)
    spotifyIcon = loadImageB64("https://storage.googleapis.com/pr-newsroom-wp/1/2018/11/Spotify_Logo_CMYK_White.png")
    spotifyBadgeColor = getSpotifyBadgeColor()
    musicLink = ""
    musicTime = 0
    explicit = ""
    albumCover = ""
    artistName = ""
    songName = ""
    viewAnimation = 0
    progress_data = {
        "progress_ms": 0,
        "duration_ms": 1,
        "pause_flag": False
    }

    if "item" in data:
        item = data["item"]
        musicLink = item["album"]["external_urls"]
        musicTime = convertMsToMin(item["duration_ms"])
        explicit = item["explicit"]
        albumCover = loadImageB64(item["album"]["images"][1]["url"])
        artistName = item["artists"][0]["name"].replace("&", "&amp;")
        songName = item["name"].replace("&", "&amp;")
        viewAnimation = len(songName) > 27
        progress_data["progress_ms"] = data["progress_ms"]
        progress_data["duration_ms"] = item["duration_ms"]
        if "pausing" in data["actions"]['disallows']:
            progress_data["pause_flag"] = data["actions"]['disallows']['pausing']
    spotifyObject = {
        "spotifyBadgeColor": spotifyBadgeColor,
        "spectrographWidth": spectrographWidth(),
        "soundVisualizerBar": soundVisualizerBar,
        "soundVisualizerCSS": soundVisualizerCSS,
        "artistName": artistName,
        "spotifyIcon": spotifyIcon,
        "viewAnimation": viewAnimation,
        "songName": songName,
        "albumCover": albumCover,
        "barColor": SPOTIFY_BAR_COLOR,
        "explicit": explicit,
        "musicTime": musicTime,
        "musicLink": musicLink,
        "progress_data": progress_data
    }
    return spotifyObject


def makeSVG(data):
    # if data == {}:
    #     recent_plays = recentlyPlayed()
    #     size_recent_play = len(recent_plays["items"])
    #     idx = random.randint(0, size_recent_play - 1)
    #     item = recent_plays["items"][idx]["track"]
    # else:
    #     item = data["item"]
    spotifyObject = setSpotifyObject(data)

    return render_template("spotifyStatus.html.j2", spotifyObject=spotifyObject)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    data = nowPlaying()
    svg = makeSVG(data)

    resp = Response(svg, mimetype="image/svg+xml")
    resp.headers["Cache-Control"] = "s-maxage=1"

    return resp


@app.route('/api/playingData')
def summary():
    return setSpotifyObject(nowPlaying())


if __name__ == "__main__":
    app.run(debug=True)
