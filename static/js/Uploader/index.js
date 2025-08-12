/**
 * 將位元組大小轉換為可閱讀的格式 (KB, MB, GB, TB, PB)。
 * * @param {number} sizeInBytes - 以位元組為單位的整數大小。
 * @returns {string} - 可閱讀的字串，例如 "10.5 MB"。
 */
function bytesToHumanReadableSize(sizeInBytes) {
  // 檢查無效輸入
  if (sizeInBytes < 0) {
    return "無效大小 (不能為負數)";
  }

  // 定義單位和對應的進位值
  const units = ["B", "KB", "MB", "GB", "TB", "PB"];
  const base = 1024;

  // 如果大小為 0，直接回傳 "0 B"
  if (sizeInBytes === 0) {
    return "0 B";
  }

  // 使用 Math.floor(Math.log(sizeInBytes) / Math.log(base)) 計算對數以確定單位
  // Math.log(x, base) 在 JavaScript 中需要用 Math.log(x) / Math.log(base) 來實現
  let i = Math.floor(Math.log(sizeInBytes) / Math.log(base));

  // 確保索引不超過單位列表的範圍
  if (i >= units.length) {
    // 使用最大的單位
    i = units.length - 1;
  }

  // 計算轉換後的值
  const humanReadableSize = sizeInBytes / Math.pow(base, i);

  // 格式化輸出，保留兩位小數（如果不是 B 的話）
  // toFixed(2) 會將數字四捨五入到兩位小數
  if (i > 0) {
    return `${humanReadableSize.toFixed(2)} ${units[i]}`;
  } else {
    // 對於 B，不需要小數
    return `${humanReadableSize} ${units[i]}`;
  }
}

document.addEventListener("DOMContentLoaded", function(event) {
    const dropZone = document.getElementById("file-dropzone")
    const fileInput = document.getElementById("file-input");

    dropZone.addEventListener("dragenter", function (e) {
        e.preventDefault();

        dropZone.classList.add("highlight");
    });

    dropZone.addEventListener("dragover", function (e) {
        e.preventDefault();
    });

    dropZone.addEventListener("dragleave", function (e) {
        e.preventDefault();

        dropZone.classList.remove("highlight");
    });

    dropZone.addEventListener("drop", function (e) {
        e.preventDefault();

        dropZone.classList.remove("highlight");

        fileInput.files = e.dataTransfer.files;
        fileInput.dispatchEvent(new Event("change"));  // Trigger the change event to update file info
    });

    dropZone.addEventListener("click", function (e) {
        fileInput.click();  // Trigger the file input click to open file dialog
    })

    fileInput.addEventListener("change", function (e) {
        const file = e.target.files.item(0);

        if (file) {
            const fileName = file.name;
            const fileSize = bytesToHumanReadableSize(file.size);
            const fileType = file.type || "(未知類型)";

            document.getElementById("file-name").textContent = fileName;
            document.getElementById("file-name-input").value = fileName;
            document.getElementById("file-size").textContent = fileSize;
            document.getElementById("file-type").textContent = fileType;

            if (file.size > 100 * 1024 * 1024) { // 超過 100 MB
                document.getElementById("file-size").classList.add("warning");
                document.getElementById("upload-button").disabled = true;
            } else {
                document.getElementById("file-size").classList.remove("warning");
                document.getElementById("upload-button").disabled = false;
            }
        }
    })

    document.getElementById("require-login-switch").addEventListener("change", function (e) {
        document.getElementById("require-login-input").value = e.target.selected;
    })

    const url = new URL(window.location.href);
    if (url.searchParams.has("success")) {
        const fileUUID = url.searchParams.get("success");
        document.getElementById("result-icon").textContent = "cloud_done"
        document.getElementById("result-container").classList.add("result-success");
        document.getElementById("result-text").innerHTML = `檔案上傳成功！你的檔案連結為 
<a href="/user_uploads/uploader/${fileUUID}" target="_blank">${fileUUID}</a>`;
    } else if (url.searchParams.has("error")) {
        const errorMessage = url.searchParams.get("error");
        document.getElementById("result-icon").textContent = "cloud_alert"
        document.getElementById("result-container").classList.add("result-error");
        document.getElementById("result-text").textContent = `檔案上傳失敗：${errorMessage}`;
    } else {
        document.getElementById("result-container").style.display = "none";
    }
})