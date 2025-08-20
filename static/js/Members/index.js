function measureHeight() {
    const refElement = document.getElementById("content-height-ref");
    const height = refElement.offsetHeight;
    document.getElementById("warning-points-history-list").style.height = `${height}px`;
}

window.addEventListener("resize", measureHeight);
window.addEventListener("load", measureHeight);