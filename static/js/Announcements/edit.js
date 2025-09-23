function checkTime() {
    const rawPinDueDate = document.getElementById("pin-until-selector").value;
    if (rawPinDueDate === "") {
        document.getElementById("pin-until-text").value = "";
        return;
    }
    const pinDueDate = new Date(rawPinDueDate);
    const pinDueDateText = document.getElementById("pin-until-text");
    if (!(pinDueDate > new Date())) {
        pinDueDateText.error = true;
        pinDueDateText.errorText = "置頂期限需在未來時間。";
    } else {
        pinDueDateText.error = false;
        pinDueDateText.errorText = "";
    }
}

function toggleDateSelector() {
    const switchElement = document.getElementById('is-pinned-switch');
    if (switchElement.selected) {
        document.getElementById('pin-until-text').style.display = 'inline-flex';
        document.getElementById('pin-until-selector-group').style.display = 'inline-flex';
        document.getElementById("pin-until-selector").disabled = false;
    } else {
        document.getElementById('pin-until-text').style.display = 'none';
        document.getElementById('pin-until-selector-group').style.display = 'none';
        document.getElementById("pin-until-selector").disabled = true;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    toggleDateSelector();
    checkTime();

    document.getElementById('is-pinned-switch').addEventListener('change', toggleDateSelector);
    document.getElementById("pin-until-selector").addEventListener("change", (event) => {
        if (document.getElementById('is-pinned-switch').selected) {
            const pinDueDateText = document.getElementById("pin-until-text");
            if (event.target.value === "") {
                pinDueDateText.value = "";
            } else {
                const pinDueDate = new Date(event.target.value);

                const year = pinDueDate.getFullYear();
                const month = (pinDueDate.getMonth() + 1).toString().padStart(2, "0");
                const day = pinDueDate.getDate().toString().padStart(2, "0");
                const hours = pinDueDate.getHours().toString().padStart(2, "0");
                const minutes = pinDueDate.getMinutes().toString().padStart(2, "0");

                pinDueDateText.value = `${year}/${month}/${day} ${hours}:${minutes}`;
            }
            checkTime();
        }
    })
    document.querySelectorAll(".submit-button").forEach((button) => {
        button.addEventListener("click", (event) => {
            if (document.getElementById("md-editor").value === "") {
                alert("請輸入公告內容。");
                return;
            }
            if (document.getElementById('is-pinned-switch').selected) {
                const pinDueDate = new Date(document.getElementById("pin-until-selector").value);
                if (!(pinDueDate > new Date())) {
                    alert("「置頂期限」需設為未來時間。");
                    return;
                }
            }
            document.getElementById("submit-type").value = event.target.id.replace("-button", "");
            document.getElementById("is-pinned").value = document.getElementById('is-pinned-switch').selected;
            document.getElementById("announcement-form").requestSubmit();
        });
    });

    try {
        document.getElementById("delete-button").addEventListener("click", (event) => {
            if (confirm("確定要刪除這則公告嗎？這個動作無法復原。")) {
                fetch(window.location.origin + "/announcement/" + document.getElementById("announcement-id").value + "/delete/", {
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
        console.log("No delete button present.");
    }
});