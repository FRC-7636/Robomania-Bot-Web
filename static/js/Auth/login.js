document.addEventListener("DOMContentLoaded", function() {
    const loginForm = document.getElementById("login-form-div");

    document.getElementById("backup-login-collapse-button").addEventListener("click", (event) => {
        if (loginForm.getAttribute("expanded")) {  // 隱藏備用登入表單
            loginForm.removeAttribute("expanded");
            event.target.removeAttribute("expanded");
        } else {  // 顯示備用登入表單
            loginForm.setAttribute("expanded", "1");
            event.target.setAttribute("expanded", "1");
        }
    });

})