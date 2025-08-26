function measureHeight() {
    const refElement = document.getElementById("content-height-ref");
    const height = refElement.offsetHeight;
    document.getElementById("meetings-container").style.height = `${height}px`;
    document.getElementById("warning-history-container").style.height = `${height}px`;
}

function resizeWarnStatus() {
    const warnStatusText = document.getElementById("warn-status-text");
    const containerWidth = document.getElementById("upcoming-meetings-list-div").offsetWidth;
    const em = parseFloat(getComputedStyle(document.documentElement).fontSize);

    warnStatusText.style.width = `${containerWidth - (1 + 0.25) * em - 24}px`;
    console.log(`${containerWidth - (1 + 0.25) * em - 24}px`)
}

window.addEventListener("resize", measureHeight);
window.addEventListener("resize", resizeWarnStatus);
window.addEventListener("load", measureHeight);
window.addEventListener("load", resizeWarnStatus);