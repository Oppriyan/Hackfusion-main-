import {MED_DB} from "../state.js";

export function initShop(){

window.renderShopGrid = function(){

const grid = document.getElementById("shopGrid");

if(!grid) return;

grid.innerHTML = MED_DB.map(m=>`

<div class="card">

<h4>${m.name}</h4>

<p>${m.cat}</p>

<strong>€${m.price}</strong>

<button onclick="addToCart('${m.name}',${m.price})">
Add to Cart
</button>

</div>

`).join("");

};

renderShopGrid();

}