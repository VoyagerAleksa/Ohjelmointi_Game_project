"use strict";
const buttons = document.querySelectorAll("button")
const audioSoundHover = new Audio("../audio/button_hover.wav")
const audioSoundClick = new Audio("../audio/button_click.wav")

buttons.forEach((button) => {
    button.addEventListener("mouseenter", function () {
        audioSoundHover.currentTime = 0
        audioSoundHover.play()
    })

    button.addEventListener("mouseleave", function () {
        audioSoundHover.pause()
        audioSoundHover.currentTime = 0
    })

    button.addEventListener("click", function () {
        audioSoundClick.currentTime = 0;
        audioSoundClick.play()
    })
})

