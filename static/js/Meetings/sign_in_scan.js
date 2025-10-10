document.addEventListener("DOMContentLoaded", function () {
    const signedInCount = document.getElementById("signed-in-count");
    const countdownTimer = document.getElementById("countdown-timer");

    const startTime = new Date(document.getElementById("sing-in-start-time").value).getTime();
    const endTime = new Date(document.getElementById("sing-in-end-time").value).getTime();
    if (startTime > Date.now()) {
        document.getElementById("countdown-head").textContent = "距離開放還有";
        setInterval(() => {
            const now = Date.now();
            const distanceSec = (startTime - now) / 1000;

            if (distanceSec <= 0) {
                window.location.reload()
            }

            const hours = Math.floor(distanceSec / 3600).toString().padStart(2, "0");
            const minutes = Math.floor((distanceSec % 3600) / 60).toString().padStart(2, "0");
            const seconds = Math.floor(distanceSec % 60).toString().padStart(2, "0");
            countdownTimer.textContent = `${hours}:${minutes}:${seconds}`;
        }, 1000)
    } else {
        const signInCountdown = setInterval(() => {
            const now = Date.now();
            const distanceSec = (endTime - now) / 1000;

            if (distanceSec <= 0) {
                document.getElementById("qrcode-content").textContent = "簽到已結束";
                countdownTimer.textContent = "00:00:00";
                clearInterval(signInCountdown);
                return;
            }

            const hours = Math.floor(distanceSec / 3600).toString().padStart(2, "0");
            const minutes = Math.floor((distanceSec % 3600) / 60).toString().padStart(2, "0");
            const seconds = Math.floor(distanceSec % 60).toString().padStart(2, "0");
            countdownTimer.textContent = `${hours}:${minutes}:${seconds}`;
        }, 1000)
    }

    // Reusable divider element
    const dividerDiv = document.createElement("div");
    dividerDiv.className = "divider";
    const verticalDividerDiv = document.createElement("div");
    verticalDividerDiv.className = "vertical-spacer";

    const recordList = document.getElementById("record-list");

    const ws = new WebSocket(
        `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/meeting/sign_in/${window.location.href.split("/")[6]}/`
    );

    ws.onopen = () => {
        console.log("WebSocket connection established.");
    }

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type !== "signin.new_record") {
            return;
        }
        const lastSignInCount = parseInt(signedInCount.textContent);
        signedInCount.textContent = (lastSignInCount + 1).toString();

        const record = data.record;

        const recordItem = document.createElement("md-list-item");
        const recordItemDiv = document.createElement("div");
        recordItemDiv.className = "record-item";
        const memberIndicator = document.createElement("div");
        memberIndicator.classList.add("record-member", "member-indicator");
        const memberImg = document.createElement("img");
        memberImg.className = "member-avatar";
        memberImg.src = record.member.avatar;
        const memberName = document.createElement("span");
        memberName.className = "member-name";
        memberName.style.color = "black";
        memberName.textContent = `${record.member.real_name} (${record.member.discord_id})`;
        memberIndicator.append(memberImg, memberName);
        const signInTime = document.createElement("span");
        signInTime.classList.add("record-item-text", "record-signed-at");
        signInTime.textContent = record.signed_in_at;
        recordItemDiv.append(memberIndicator, verticalDividerDiv.cloneNode(), signInTime);
        recordItem.appendChild(recordItemDiv);

        if (recordList.childNodes.length < 4) {
            recordList.append(dividerDiv.cloneNode(), recordItem);
        } else {
            recordList.insertBefore(recordItem, recordList.childNodes[2]);
            recordList.insertBefore(dividerDiv.cloneNode(), recordItem);
        }
    }

    ws.onclose = (event) => {
        console.log(`WebSocket connection closed. (Code: ${event.code}, Reason: ${event.reason})`);
        alert(`與伺服器的連線中斷，因此簽到狀態可能不會更新。請重新載入此頁面。\n(${event.code}: ${event.reason})`);
    }
})