"use strict";
const buttons = document.querySelectorAll("button")
const audioSoundHover = new Audio("../audio/button_hover.wav")
const audioSoundClick = new Audio("../audio/button_click.wav")
const audioAmbient = new Audio("../audio/ambient.wav")
const audioGameTheme = new Audio("../audio/game_theme.wav")

function playGameTheme() {
    audioGameTheme.volume = 0.2
    audioGameTheme.loop = true
    audioGameTheme.play()
}

function playAmbient() {
    audioAmbient.volume = 0.4
    audioAmbient.loop = true
    audioAmbient.play()
}
function stopMusic(){
    audioAmbient.pause()
    audioGameTheme.pause()
}
window.Sound = {
    playGameTheme,
    playAmbient,
    stopMusic
}



buttons.forEach((button) => {
    button.addEventListener("mouseenter", function () {
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
        audioSoundClick.currentTime = 0;
        audioSoundClick.play()
    })
})

