document.addEventListener("DOMContentLoaded", () => {
    const orderBy = new URLSearchParams(window.location.search).get("order_by");
    const orderByAbs = orderBy.replace("-", "");
    const upOrDown = orderBy.startsWith("-") ? "▲" : "▼";

    if (["pk", "discord_id", "real_name", "warning_points", "email_address", "gen"].includes(orderByAbs)) {
        const headId = `${orderByAbs}-head`
        const headElement = document.getElementById(headId);

        const originalText = headElement.innerText;

        headElement.innerText = `${originalText} ${upOrDown}`;
    }

    const headElements = document.querySelectorAll("span[id$='-head-click']");
    headElements.forEach(headElement => {
        headElement.addEventListener("click", () => {
            const myKey = headElement.id.replace("-head-click", "");
            let nextKey;
            if (orderByAbs.includes(myKey)) {
                nextKey = orderBy.startsWith("-") ? myKey : `-${myKey}`;
            } else {
                nextKey = myKey;
            }
            console.log(nextKey);

            let url = new URL(window.location.href);
            url.searchParams.set("order_by", nextKey);
            window.location.href = url.href;
        })
    })
})