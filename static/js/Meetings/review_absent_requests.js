let EDITED_REQUESTS = {};

function checkEditedRequests() {
    const submitButton = document.getElementById("submit-button");

    submitButton.disabled = (Object.keys(EDITED_REQUESTS).length === 0);
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("submit-button").addEventListener("click", () => {
        let formData = new FormData();
        formData.append("csrfmiddlewaretoken", document.querySelector('input[name="csrfmiddlewaretoken"]').value);
        formData.append("edited_requests", JSON.stringify(EDITED_REQUESTS));

        fetch(`${window.location.origin}/meeting/${document.getElementById("meeting-id").value}/review_absent_requests_api/`, {
            method: "POST",
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                alert(`提交時發生錯誤，請稍後再試。\n錯誤訊息：${response.body.toString()}`);
            } else {
                alert("已成功提交請假審核結果。");
                window.location.reload();
            }
        });
    });

    const selectElements = document.querySelectorAll('[id^="action_select"]');
    selectElements.forEach(element => {
        let reqId = element.id.split("-")[1];

        element.addEventListener("change", () => {
            if (element.value === "none") {
                document.getElementById(`action_comment-${reqId}`).disabled = true;
                if (reqId in EDITED_REQUESTS) {
                    delete EDITED_REQUESTS[reqId];
                }
            } else {
                document.getElementById(`action_comment-${reqId}`).disabled = false;
                if (!(reqId in EDITED_REQUESTS)) {
                    EDITED_REQUESTS[reqId] = {
                        status: element.value,
                        comment: document.getElementById(`action_comment-${reqId}`).value,
                    };
                } else {
                    EDITED_REQUESTS[reqId].status = element.value;
                }
            }
            checkEditedRequests()
        })
    })

    const commentElements = document.querySelectorAll('[id^="action_comment"]');
    commentElements.forEach(element => {
        let reqId = element.id.split("-")[1];

        element.addEventListener("change", () => {
            if (reqId in EDITED_REQUESTS) {
                EDITED_REQUESTS[reqId].comment = element.value;
            }
            checkEditedRequests()
        })
    })
})