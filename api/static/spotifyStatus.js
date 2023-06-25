let progressData = JSON.parse(document.getElementById("progress_data_div").dataset.geocode);
let progressMs = progressData["progress_ms"];
let durationMs = progressData["duration_ms"];
let pauseFlag = progressData["pause_flag"];
let count = 0;

function formatTime(timeMs) {
    const minutes = Math.floor(timeMs / 60000);
    const seconds = Math.floor((timeMs % 60000) / 1000);
    return (minutes < 10 ? '0' : '') + minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
}

function updateProgress() {
    let progressElement = document.getElementById('progress');
    let progressTimeElement = document.getElementById('progress-time');
    let progressPercent = (progressMs / durationMs) * 100;
    progressElement.style.width = progressPercent + '%';
    progressTimeElement.textContent = formatTime(progressMs);
    if (pauseFlag) {
        return;
    }
    // 自动递增进度
    if (progressMs < durationMs) {
        progressMs += 1000;
        setTimeout(updateProgress, 1000)
    }
    // count ++ ;
    // if(count % 3 === 0){
    //     requestProgress()
    // }
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
    progressMs = data["progress_ms"];
    durationMs = data["duration_ms"];
    pauseFlag = data["pause_flag"];
}