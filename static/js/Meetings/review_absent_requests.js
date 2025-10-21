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
        .then((response) => response.json())
        .then(data => {
            console.log(data)
            if (data.length === 0) {
                alert("已成功提交假單審核結果。");
            } else {
                let conflictString = "下列成員的假單在提交時已由其他人審核，因此沒有生效：";
                for (const conflict of data) {
                    conflictString += `\n${conflict[0]} 已由 ${conflict[1]} 審核為 ${conflict[2]}`;
                }
                alert(conflictString);
            }
            window.location.reload();
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