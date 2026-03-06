import {NOTIFS} from "../state.js";

export function initNotifications(){

const list = document.getElementById("notifList");

if(!list) return;

const renderNotifs = () => {
  list.innerHTML = NOTIFS.map(n => `
<div class="notif-item">
<span>${n.icon}</span>
<div>
<strong>${n.title}</strong>
<small>${n.time}</small>
</div>
</div>
`).join("");
};

renderNotifs();

window.toggleNotif = function() {
  const notifDrop = document.getElementById("notifDrop");
  if (notifDrop) {
    notifDrop.classList.toggle("show");
  }
};

window.clearNotifs = function() {
  if (confirm("Clear all notifications?")) {
    NOTIFS.length = 0;
    renderNotifs();
    document.getElementById("notifDot")?.remove();
  }
};

}