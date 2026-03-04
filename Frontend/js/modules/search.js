import {MED_DB} from "../state.js";

export function initSearch(){

const input = document.getElementById("heroSearch");

if(!input) return;

input.addEventListener("input",()=>{

const q = input.value.toLowerCase();

const res = MED_DB.filter(m=>
m.name.toLowerCase().includes(q)
);

console.log("search results",res);

});

}