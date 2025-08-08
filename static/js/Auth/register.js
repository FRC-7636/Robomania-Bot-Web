document.addEventListener("DOMContentLoaded", () => {
    let passwordInput = document.getElementById("password-input");
    let confirmPasswordInput = document.getElementById("confirm-password-input");

    function markPasswordMismatch() {
        let password = passwordInput.value;
        let confirmPassword = confirmPasswordInput.value;

        if (password !== confirmPassword) {
            confirmPasswordInput.error = true;
            confirmPasswordInput.errorText = "密碼不吻合";
        } else {
            confirmPasswordInput.error = false;
            confirmPasswordInput.errorText = "";
        }
    }

    passwordInput.addEventListener("input", markPasswordMismatch);
    confirmPasswordInput.addEventListener("input", markPasswordMismatch);
})