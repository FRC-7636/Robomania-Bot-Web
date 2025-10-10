function checkTime() {
    const rawStartTime = document.getElementById("start-time-selector").value;
    if (rawStartTime === "") {
        return true;
    }
    const startTime = new Date(rawStartTime).getTime();

    const startTimeText = document.getElementById("start-time-text");
    if (startTime < Date.now()) {
        startTimeText.error = true;
        startTimeText.errorText = "開放時間需在現在時間之後。";
        return false;
    } else {
        startTimeText.error = false;
        startTimeText.errorText = "";
        return true;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById("start-time-selector").addEventListener("change", function (event) {
        checkTime();
        const startTimeText = document.getElementById("start-time-text");
        if (event.target.value === "") {
            startTimeText.value = "";
        } else {
            const startTime = new Date(event.target.value);

            const year = startTime.getFullYear();
            const month = (startTime.getMonth() + 1).toString().padStart(2, "0");
            const day = startTime.getDate().toString().padStart(2, "0");
            const hours = startTime.getHours().toString().padStart(2, "0");
            const minutes = startTime.getMinutes().toString().padStart(2, "0");

            startTimeText.value = `${year}/${month}/${day} ${hours}:${minutes}`;
        }
    })

    document.getElementById("submit-button").addEventListener("click", function (event) {
        if (checkTime()) {
            document.getElementById("sign-in-create-form").requestSubmit();
        }
    })
})