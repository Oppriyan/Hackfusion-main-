export function initToast() {
  window.toast = function (msg, type = "blue") {
    const wrap = document.getElementById("toastWrap");
    if (!wrap) return;

    const t = document.createElement("div");
    t.className = "toast " + type;
    t.innerText = msg;
    wrap.appendChild(t);

    setTimeout(() => {
      t.remove();
    }, 3500);
  };

  // Alias for toast
  window.showToast = function (msg, type = "info") {
    // Map message types to toast types
    const toastType =
      type === "error"
        ? "red"
        : type === "success"
          ? "green"
          : type === "warning"
            ? "yellow"
            : "blue";

    window.toast(msg, toastType);
  };
}
