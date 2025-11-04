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
    const announcements = JSON.parse(document.getElementById("pinned-announcements-data").textContent);
    console.log(announcements);

    const annText = document.getElementById("announcement-content");
    const annLink = document.getElementById("announcement-link");
    // Initial announcement
    if (announcements.length === 0) {
        annLink.href = "#";
        annText.textContent = "(目前沒有釘選中的公告)";
    } else {
        annText.textContent = `【${announcements[0].title}】${announcements[0].content}`;
        annLink.href = `{% url "announcement_info" 0 %}`.replace('/0/', `/${announcements[0].id}/`);
        let i = 1;
        if (announcements.length > 1) {
            setInterval(() => {
                setTimeout(() => {
                    annText.style.opacity = "0";
                }, 500)
                setTimeout(() => {
                    annText.textContent = `【${announcements[i].title}】${announcements[i].content}`;
                    annLink.href = `{% url "announcement_info" 0 %}`.replace('/0/', `/${announcements[i].id}/`);
                    annText.style.opacity = "1";
                    i = (i + 1) % announcements.length;
                }, 1000)
            }, 10000);
        }
    }

    const searchParams = new URLSearchParams(window.location.search);
    const syncResult = searchParams.get("sync");

    if (syncResult === "success") {
        alert("頭像同步完成！");
    } else if (syncResult === "failed") {
        alert("頭像同步失敗。\n請確認你登入的 Discord 帳號為你的帳號，並且在授權頁面按下「授權」。");
    }
    window.history.replaceState({}, document.title, "/");
});