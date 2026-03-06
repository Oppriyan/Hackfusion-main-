import {NOTIFS} from "../state.js";

export function initNotifications(){

const list = document.getElementById("notifList");

if(!list) return;

list.innerHTML = NOTIFS.map(n => `
<div class="notif-item">
<span>${n.icon}</span>
<div>
<strong>${n.title}</strong>
<small>${n.time}</small>
</div>
</div>
`).join("");

}