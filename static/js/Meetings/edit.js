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

function checkNotifyTime() {
    const notifyTimeInput = document.getElementById("discord-notify-time-input");
    const inputValue = notifyTimeInput.value;
    const startTime = new Date(document.getElementById("start-time-selector").value).getTime();
    if (inputValue === "" || isNaN(inputValue) || parseInt(inputValue) < 0) {
        notifyTimeInput.error = true;
        notifyTimeInput.errorText = "請輸入有效的正整數。";
    } else if (Date.now() + parseInt(inputValue) * 60000 > startTime) {
        notifyTimeInput.error = true;
        notifyTimeInput.errorText = "通知時間必須早於會議開始時間。";
    } else {
        notifyTimeInput.error = false;
        notifyTimeInput.errorText = "";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("start-time-selector").addEventListener("change", function (event) {
        checkTime();
        checkNotifyTime();
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

    document.getElementById("location-input").addEventListener("input", function (event) {
        const dcSelect = document.getElementById(`select-${event.target.value}`);
        const selector = document.getElementById("discord-vc-autofill");
        if (dcSelect) {
            selector.select(event.target.value);
        } else {
            selector.value = "";
        }
    })

    document.getElementById("discord-vc-autofill").addEventListener("change", (event) => {
        console.log(event.target.value)
        document.getElementById("location-input").value = event.target.value;
    })

    document.getElementById("everyone-role").addEventListener("click", (event) => {
        const normalRoles = document.getElementsByClassName("normal-role");
        if (event.target.selected) {
            Array.from(normalRoles).forEach((element) => {
                element.disabled = true;
            });
        } else {
            Array.from(normalRoles).forEach((element) => {
                element.disabled = false;
            });
        }
    })

    document.getElementById("discord-notify-time-input").addEventListener("change", checkNotifyTime)

    document.getElementById("submit-button").addEventListener("click", function () {
        checkNotifyTime()
        // Serialize role selections
        const rolesInput = document.getElementById("discord-mentions-input");
        let rolesString;
        if (document.getElementById("everyone-role").selected) {
            rolesString = "[\"@everyone\"]";
        } else {
            const selectedRoles = [];
            const normalRoles = document.getElementsByClassName("normal-role");
            Array.from(normalRoles).forEach((element) => {
                if (element.selected) {
                    selectedRoles.push(element.getAttribute("role-id"));
                }
            });
            rolesString = JSON.stringify(selectedRoles);
        }
        // @everyone if none selected
        if (rolesString === "[]") {
            rolesString = "[\"@everyone\"]";
        }
        rolesInput.value = rolesString;
        document.getElementById("meeting-form").requestSubmit();
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