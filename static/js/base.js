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
})