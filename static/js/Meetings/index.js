document.addEventListener("DOMContentLoaded", () => {
    const signInList = document.getElementById("sign-in-list-content");
    const absentReqList = document.getElementById("absent-request-list-content");
    const recordList = document.getElementById("record-list-content");

    if (signInList !== null) {  // 檢查簽到階段清單是否存在
        document.getElementById("sign-in-collapse-button").addEventListener("click", (event) => {
            if (signInList.getAttribute("expanded")) {  // 隱藏簽到清單
                signInList.removeAttribute("expanded");
                event.target.removeAttribute("expanded");
            } else {  // 顯示簽到清單
                signInList.setAttribute("expanded", "1");
                event.target.setAttribute("expanded", "1");
            }
        });
    }

    if (recordList !== null) {
        document.getElementById("record-collapse-button").addEventListener("click", (event) => {
            if (recordList.getAttribute("expanded")) {  // 隱藏簽到清單
                recordList.removeAttribute("expanded");
                event.target.removeAttribute("expanded");
            } else {  // 顯示簽到清單
                recordList.setAttribute("expanded", "1");
                event.target.setAttribute("expanded", "1");
            }
        });
    }

    document.getElementById("absent-request-collapse-button").addEventListener("click", (event) => {
        if (absentReqList.getAttribute("expanded")) {
            absentReqList.removeAttribute("expanded");
            event.target.removeAttribute("expanded");
        } else {
            absentReqList.setAttribute("expanded", "1");
            event.target.setAttribute("expanded", "1");
        }
    });
});