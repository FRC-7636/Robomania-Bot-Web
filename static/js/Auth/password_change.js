document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("submit-button").addEventListener("click", function() {
        const newPasswordInput = document.getElementById("new-password-input");
        const confirmNewPasswordInput = document.getElementById("new-password-confirm-input");

        function markPasswordMismatch() {
            let password = newPasswordInput.value;
            let confirmPassword = confirmNewPasswordInput.value;

            if (password !== confirmPassword) {
                confirmNewPasswordInput.error = true;
                confirmNewPasswordInput.errorText = "密碼不吻合";
            } else {
                confirmNewPasswordInput.error = false;
                confirmNewPasswordInput.errorText = "";
        }
    }

    newPasswordInput.addEventListener("input", markPasswordMismatch);
    confirmNewPasswordInput.addEventListener("input", markPasswordMismatch);
    })

    const url = new URL(window.location.href);
    if (url.searchParams.has("error")) {
        document.getElementById("error-text").textContent = url.searchParams.get("error");
        document.getElementById("error-container").style.display = "flex";
    } else {
        document.getElementById("error-container").style.display = "none";
    }
})