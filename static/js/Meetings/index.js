document.addEventListener("DOMContentLoaded", () => {
    const signInList = document.getElementById("sign-in-list-content");
    document.getElementById("collapse-button").addEventListener("click", (event) => {
        if (signInList.getAttribute("expanded")) {  // 隱藏簽到清單
            signInList.removeAttribute("expanded");
            event.target.removeAttribute("expanded");
        } else {  // 顯示簽到清單
            signInList.setAttribute("expanded", "1");
            event.target.setAttribute("expanded", "1");
        }
    });
});