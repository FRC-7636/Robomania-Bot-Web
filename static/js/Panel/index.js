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

document.addEventListener("DOMContentLoaded", () => {
    const searchParams = new URLSearchParams(window.location.search);
    const syncResult = searchParams.get("sync");

    if (syncResult === "success") {
        alert("頭像同步完成！");
    } else if (syncResult === "failed") {
        alert("頭像同步失敗。\n請確認你登入的 Discord 帳號為你的帳號，並且在授權頁面按下「授權」。");
        window.history.replaceState({}, document.title, "/");
    }
});