function checkTime() {
    const rawStartTime = document.getElementById("start-time-selector").value;
    const rawEndTime = document.getElementById("end-time-selector").value;
    if (rawStartTime === "" || rawEndTime === "") {
        return; // No end time selected, no need to check
    }
    const startTime = new Date(rawStartTime).getTime();
    const endTime = new Date(rawEndTime).getTime();

    const startTimeText = document.getElementById("start-time-text");
    const endTimeText = document.getElementById("end-time-text");
    if (endTime <= startTime) {
        startTimeText.error = true;
        startTimeText.errorText = "結束時間需在開始時間之後。";
        endTimeText.error = true;
        endTimeText.errorText = "結束時間需在開始時間之後。";
    } else {
        startTimeText.error = false;
        startTimeText.errorText = "";
        endTimeText.error = false;
        endTimeText.errorText = "";
    }
}

document.addEventListener("DOMContentLoaded", function () {
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

    document.getElementById("end-time-selector").addEventListener("change", function (event) {
        checkTime();
        const endTimeText = document.getElementById("end-time-text");
        if (event.target.value === "") {
            endTimeText.value = "";
        } else {
            const endTime = new Date(event.target.value);

            const year = endTime.getFullYear();
            const month = (endTime.getMonth() + 1).toString().padStart(2, "0");
            const day = endTime.getDate().toString().padStart(2, "0");
            const hours = endTime.getHours().toString().padStart(2, "0");
            const minutes = endTime.getMinutes().toString().padStart(2, "0");

            endTimeText.value = `${year}/${month}/${day} ${hours}:${minutes}`;
        }
    })

    document.getElementById("can-absent-switch").addEventListener("change", function (event) {
        document.getElementById("can-absent-bool").value = event.target.selected;
    })

    document.getElementById("submit-button").addEventListener("click", function () {
        document.getElementById("meeting-form").submit();
    })

    try {
        document.getElementById("delete-button").addEventListener("click", function () {
            const confirmDelete = confirm("確定要刪除這個會議嗎？這個動作無法復原。");
            if (confirmDelete) {
                fetch(window.location.origin + "/meeting/" + document.getElementById("meeting-id").value + "/delete/", {
                    method: "DELETE",
                    headers: {"X-CSRFToken": document.getElementsByName("csrfmiddlewaretoken")[0].value},
                    mode: "same-origin",
                }).then(response => {
                    if (response.ok) {
                        window.location.href = window.location.origin;
                    } else {
                        alert("刪除會議失敗，請稍後再試。");
                    }
                })
            }
        })
    } catch (error) {
        console.log("No delete button present.")
    }
})