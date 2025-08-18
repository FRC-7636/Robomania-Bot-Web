function measureHeight() {
    const refElement = document.getElementById("content-height-ref");
    const height = refElement.offsetHeight;
    document.getElementById("meetings-container").style.height = `${height}px`;
    document.getElementById("warning-history-container").style.height = `${height}px`;
}

window.addEventListener("resize", measureHeight);
window.addEventListener("load", measureHeight);