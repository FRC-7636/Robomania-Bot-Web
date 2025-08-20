document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("submit-button").addEventListener("click", () => {
        const pointsInput = document.getElementById("points-input");

        if (parseFloat(pointsInput.value) === 0.0) {
            pointsInput.error = true;
            pointsInput.errorText = "點數不得為 0。";
        } else {
            pointsInput.error = false;
            pointsInput.errorText = "";
            document.getElementById("warning-points-form").requestSubmit();
        }
    })

    document.getElementById("rule-selector").addEventListener("change", (e) => {
        const rawRule = e.target.value;
        const reasonInput = document.getElementById("reason-input");
        const pointsInput = document.getElementById("points-input");
        const notesInput = document.getElementById("notes-input");

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
    })
})