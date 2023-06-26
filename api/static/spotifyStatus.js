let spotifyData = JSON.parse(document.getElementById("spotify_data_div").dataset.geocode);
let refreshSong = false;
let progressMs = spotifyData["progress_data"]["progress_ms"];
let durationMs = spotifyData["progress_data"]["duration_ms"];
let pauseFlag = spotifyData["progress_data"]["pause_flag"];
let songName = spotifyData["songName"];
let artist = spotifyData["artistName"];
let albumCover = spotifyData["albumCover"];
let viewAnimation = spotifyData["viewAnimation"];
let count = 0;

function formatTime(timeMs) {
    const minutes = Math.floor(timeMs / 60000);
    const seconds = Math.floor((timeMs % 60000) / 1000);
    return (minutes < 10 ? '0' : '') + minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
}

function updateProgress() {
    let refreshTime = pauseFlag ? 5000 : 1000;
    if (pauseFlag) {
        requestProgress()
    } else {
        let progressElement = document.getElementById('progress');
        let progressTimeElement = document.getElementById('progress-time');
        let progressPercent = (progressMs / durationMs) * 100;
        progressElement.style.width = progressPercent + '%';
        progressTimeElement.textContent = formatTime(progressMs);
        if (refreshSong) {
            let artistElement = document.getElementById('artist');
            let albumCoverElement = document.getElementById('albumCover');
            let durationTimeElement = document.getElementById('durationTime');
            durationTimeElement.textContent = formatTime(durationMs);
            buildSongName(viewAnimation, songName);
            artistElement.textContent = artist;
            albumCoverElement.setAttribute("src", "data:image/png;base64, " + albumCover);
            refreshSong = false;
        }
        count++;
        // 自动递增进度
        if (progressMs < durationMs) {
            progressMs += 1000;
            console.log("setTimeout", count, progressMs)
        }else {
            requestProgress()
            console.log("nextOne", count, progressMs)
        }
        if (count % 15 === 0) {
            requestProgress()
            console.log("refreshData", count, progressMs)
        }
    }
    setTimeout(updateProgress, refreshTime)
}

updateProgress();


function requestProgress() {
    fetch('/api/playingData') //
        .then(response => response.json())
        .then(data => {
            refresh(data)
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function refresh(data) {
    progressMs = data["progress_data"]["progress_ms"];
    durationMs = data["progress_data"]["duration_ms"];
    pauseFlag = data["progress_data"]["pause_flag"];
    if (songName !== data["songName"]) {
        refreshSong = true;
        songName = data["songName"];
        artist = data["artistName"];
        albumCover = data["albumCover"];
        viewAnimation = data["viewAnimation"];
    }

}

function buildSongName(viewAnimation, songName) {

    let songNameElement = document.getElementById('song-name');
    if (viewAnimation) {
        songNameElement.innerHTML = "<div class=\"song-title-long\"><p class=\"title title-animation\">\n" +
            "                                          <span>" + songName + "</span>\n" +
            "                                        </p></div>";
    } else {
        songNameElement.innerHTML = "<div class=\"song\"><span>" + songName + "</span></div>";
    }
}
