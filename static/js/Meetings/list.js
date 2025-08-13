document.addEventListener("DOMContentLoaded", () => {
    const orderBy = new URLSearchParams(window.location.search).get("order_by");
    const orderByAbs = orderBy.replace("-", "");
    const upOrDown = orderBy.startsWith("-") ? "▲" : "▼";

    if (["pk", "name", "host", "can_absent"].includes(orderByAbs)) {
        const headId = `${orderByAbs}-head`
        const headElement = document.getElementById(headId);

        const originalText = headElement.innerText;

        headElement.innerText = `${originalText} ${upOrDown}`;
    } else if (["start_time", "end_time"].includes(orderByAbs)) {
        const headElement = document.getElementById("time-head")

        const originalText = headElement.innerText;

        if (orderByAbs.startsWith("start")) {
            headElement.innerText = `${originalText} S${upOrDown}`;
        } else {
            headElement.innerText = `${originalText} E${upOrDown}`;
        }
    }

    const headElements = document.querySelectorAll("span[id$='-head-click']");
    headElements.forEach(headElement => {
        headElement.addEventListener("click", () => {
            const myKey = headElement.id.replace("-head-click", "");
            let nextKey;
            if (orderByAbs.includes(myKey)) {
                if (myKey === "time") {
                    const timeOrder = ["start_time", "-start_time", "end_time", "-end_time"];
                    nextKey = timeOrder[(timeOrder.indexOf(orderBy) + 1)] || timeOrder[0];
                } else {
                    nextKey = orderBy.startsWith("-") ? myKey : `-${myKey}`;
                }
            } else {
                if (myKey === "time") {
                    nextKey = "start_time";
                } else {
                    nextKey = myKey;
                }
            }
            console.log(nextKey);

            let url = new URL(window.location.href);
            url.searchParams.set("order_by", nextKey);
            window.location.href = url.href;
        })
    })
})