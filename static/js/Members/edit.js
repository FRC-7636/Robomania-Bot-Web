document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("submit-button").addEventListener("click", () => {
        const chips = document.getElementsByTagName("md-filter-chip")
        let groups = []
        for (const chip of chips) {
            if (chip.selected) {
                groups.push(chip.label)
            }
        }
        document.getElementById("groups-input").value = JSON.stringify(groups)
    })
})