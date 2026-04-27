"use strict";
const buttons = document.querySelectorAll("button")
const audioSoundHover = new Audio("../audio/button_hover.wav")
const audioSoundClick = new Audio("../audio/button_click.wav")
const audioAmbient = new Audio("../audio/ambient.wav")
const audioGameTheme = new Audio("../audio/game_theme.wav")

let soundEnabled = true

let wasPlaying = {
    ambient: false,
    gameTheme: false
}

function setSound(state) {
    soundEnabled = state
    if (!soundEnabled){
        wasPlaying.ambient = !audioAmbient.paused;
        wasPlaying.gameTheme = !audioGameTheme.paused;
        stopAllSounds()
        return
    }
    if (wasPlaying.ambient) {
        audioAmbient.play().catch(() => {});
    }
    if (wasPlaying.gameTheme) {
    audioGameTheme.play().catch(() => {});
    }
}

function stopAllSounds() {
  [audioSoundHover, audioSoundClick, audioAmbient, audioGameTheme].forEach(audio => {
    audio.pause();
    audio.currentTime = 0;
  });
}

function playGameTheme() {
    if (!soundEnabled) return;
    audioGameTheme.volume = 0.2
    audioGameTheme.loop = true
    audioGameTheme.play().catch(() => {});
}

function playAmbient() {
    if (!soundEnabled) return;
    audioAmbient.volume = 0.4
    audioAmbient.loop = true
    audioAmbient.play().catch(() => {});
}
function stopMusic(){
    audioAmbient.pause()
    audioGameTheme.pause()
}
window.Sound = {
    playGameTheme,
    playAmbient,
    stopMusic,
    setSound
}



buttons.forEach((button) => {
    button.addEventListener("mouseenter", function () {
        if (!soundEnabled) return;
        audioSoundHover.volume = 0.7
        audioSoundHover.currentTime = 0
        audioSoundHover.play()
    })

    button.addEventListener("mouseleave", function () {
        audioSoundClick.volume = 0.5
        audioSoundHover.pause()
        audioSoundHover.currentTime = 0
    })

    button.addEventListener("click", function () {
        if (!soundEnabled) return;
        audioSoundClick.currentTime = 0;
        audioSoundClick.play()
    })
})

