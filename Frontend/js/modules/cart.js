import {cartItems} from "../state.js";

export function initCart(){

window.addToCart = function(name,price){

const existing = cartItems.find(i=>i.name===name);

if(existing){

existing.qty++;

}else{

cartItems.push({name,price,qty:1});

}

renderCart();

};

window.renderCart = function(){

const el = document.getElementById("cartItems");

if(!el) return;

el.innerHTML = cartItems.map((c,i)=>`

<div>

${c.name}

x${c.qty}

<button onclick="removeCartItem(${i})">x</button>

</div>

`).join("");

};

window.removeCartItem = function(i){

cartItems.splice(i,1);

renderCart();

};

}