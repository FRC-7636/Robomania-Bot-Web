document.addEventListener("DOMContentLoaded", function(e) {
    if (document.getElementById("logout-btn") !== null) {
        document.getElementById("logout-btn").addEventListener("click", function () {
            window.location.href = "/accounts/logout";
        })
    }

    if (document.getElementById("login-btn") !== null) {
        document.getElementById("login-btn").addEventListener("click", function () {
            window.location.href = "/accounts/login";
        })
    }

    document.getElementById("collapse-btn").addEventListener("click", function (e) {
        if (e.target.classList.contains("collapsed")) {
            e.target.classList.remove("collapsed");
            e.target.textContent = "收合 ↑";
            document.getElementsByTagName("header")[0].classList.remove("collapsed");
        }
        else {
            e.target.classList.add("collapsed");
            e.target.textContent = "展開 ↓";
            document.getElementsByTagName("header")[0].classList.add("collapsed");
        }
    })
})