document.addEventListener("DOMContentLoaded", () => {
    const submitButton = document.getElementById("submit-button");
    const genInput = document.getElementById("gen-input");
    const ruleSelector = document.getElementById("rule-selector");
    const reasonInput = document.getElementById("reason-input");
    const pointsInput = document.getElementById("points-input");
    const notesInput = document.getElementById("notes-input");

    function checkboxToList() {
        const checkboxes = document.querySelectorAll('[id^="checkbox-"]');
        let ids = [];
        checkboxes.forEach((checkbox) => {
            if (checkbox.checked) {
                ids.push(parseInt(checkbox.id.slice(9)));
            }
        });
        document.getElementById("member-ids-input").value = JSON.stringify(ids);

        return ids;
    }

    function formIsSubmittable() {
        if (checkboxToList().length === 0) {
            console.log("No members selected");
            return false;
        }
        if (genInput.value === "" && ruleSelector.value === "") {
            console.log("No changes specified");
            return false;
        }
        if (!(genInput.reportValidity() && pointsInput.reportValidity() && notesInput.reportValidity())) {
            console.log("Form inputs are invalid");
            return false;
        }
        if (ruleSelector.value === "custom" && notesInput.value === "") {
            console.log("Notes required for custom rule");
            return false;
        }
        return true;
    }

    function toggleSubmitButton() {
        submitButton.disabled = !formIsSubmittable();
    }

    document.querySelectorAll('[id^="checkbox-"]').forEach((checkbox) => {
        checkbox.addEventListener("change", toggleSubmitButton);
    });

    genInput.addEventListener("input", toggleSubmitButton);
    pointsInput.addEventListener("input", toggleSubmitButton);
    notesInput.addEventListener("change", toggleSubmitButton);

    ruleSelector.addEventListener("change", () => {
        const rawRule = ruleSelector.value;

        if (rawRule === "") {
            reasonInput.value = "";
            pointsInput.value = "";
            pointsInput.readOnly = true;
            notesInput.required = false;
            reasonInput.disabled = true;
            pointsInput.disabled = true;
            notesInput.disabled = true;
        } else {
            reasonInput.disabled = false;
            pointsInput.disabled = false;
            notesInput.disabled = false;
            if (rawRule === "custom") {
                reasonInput.value = "非隊規事項";
                pointsInput.value = "";
                pointsInput.readOnly = false;
                notesInput.required = true;
            } else {
                const rule = rawRule.split(" 點 - ");
                reasonInput.value = rule[1];
                pointsInput.value = rule[0];
                pointsInput.readOnly = true;
                notesInput.required = false;
            }
        }
        toggleSubmitButton();
    })

    submitButton.addEventListener("click", () => {
        if (!formIsSubmittable()) {
            alert("請至少選取 1 位成員，並進行至少一項操作。")
            return;
        }
        const ids = checkboxToList();
        console.log(ids);

        let memberConfirmMsg = `請確認要對下列 ${ids.length} 位成員進行操作：`;
        for (const id of ids) {
            const memberName = document.getElementById(`real-name-${id}`).innerText;
            const discordId = document.getElementById(`discord-id-${id}`).innerText;
            memberConfirmMsg += `\n • ${memberName} (${discordId})`;
        }

        let operationConfirmMsg = "請確認要進行以下操作：";
        if (genInput.value !== "") {
            operationConfirmMsg += `\n • 屆別：設為第 ${genInput.value} 屆`;
        }
        if (ruleSelector.value !== "") {
            const points = pointsInput.value;
            const reason = reasonInput.value;
            const notes = notesInput.value;
            operationConfirmMsg += `\n • 記/銷點：${points} 點 - ${reason}`;
            if (notes !== "") {
                operationConfirmMsg += ` (${notes})`;
            }
        }

        if (confirm(memberConfirmMsg) && confirm(operationConfirmMsg)) {
            document.getElementById("bulk-edit-form").requestSubmit();
        }
    });
});