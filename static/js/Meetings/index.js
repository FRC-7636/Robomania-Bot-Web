document.addEventListener("DOMContentLoaded", () => {
    const signInList = document.getElementById("sign-in-list-content");
    const absentReqList = document.getElementById("absent-request-list-content");

    document.getElementById("sign-in-collapse-button").addEventListener("click", (event) => {
        if (signInList.getAttribute("expanded")) {  // 隱藏簽到清單
            signInList.removeAttribute("expanded");
            event.target.removeAttribute("expanded");
        } else {  // 顯示簽到清單
            signInList.setAttribute("expanded", "1");
            event.target.setAttribute("expanded", "1");
        }
    });

    document.getElementById("absent-request-collapse-button").addEventListener("click", (event) => {
        if (absentReqList.getAttribute("expanded")) {  // 隱藏簽到清單
            absentReqList.removeAttribute("expanded");
            event.target.removeAttribute("expanded");
        } else {  // 顯示簽到清單
            absentReqList.setAttribute("expanded", "1");
            event.target.setAttribute("expanded", "1");
        }
    });
});