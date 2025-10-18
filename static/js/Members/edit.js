document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("add-job-button").addEventListener("click", () => {
        const jobInput = document.getElementById("job-input");
        const job = jobInput.value.trim();
        if (job === "") {
            jobInput.error = true;
            jobInput.errorText = "請提供職務名稱。";
            return;
        } else {
            jobInput.error = false;
            jobInput.errorText = "";
        }
        const chips = document.getElementsByClassName("job-chip");
        let jobs = [];
        for (const chip of chips) {
            jobs.push(chip.label);
        }
        if (jobs.includes(job)) {
            jobInput.error = true;
            jobInput.errorText = "此職務已存在。";
            return;
        }
        const newJobItem = document.createElement("md-filter-chip");
        newJobItem.className = "job-chip";
        newJobItem.label = job;
        newJobItem.selected = true;
        document.getElementById("job-list").appendChild(newJobItem);
        jobInput.value = "";
    })

    document.getElementById("submit-button").addEventListener("click", () => {
        const jobChips = document.getElementsByClassName("job-chip");
        let jobs = []
        for (const chip of jobChips) {
            if (chip.selected) {
                jobs.push(chip.label)
            }
        }
        document.getElementById("jobs-input").value = JSON.stringify(jobs)
        const deptChips = document.getElementsByClassName("dept-chip");
        let groups = []
        for (const chip of deptChips) {
            if (chip.selected) {
                groups.push(chip.label)
            }
        }
        document.getElementById("groups-input").value = JSON.stringify(groups)

        document.getElementById("member-editor-form").requestSubmit();
    })
})