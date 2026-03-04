export function initChatbot(){

const input = document.getElementById("chatTi");

if(!input) return;

window.sendChatMsg = function(){

const v = input.value.trim();

if(!v) return;

console.log("chat:",v);

input.value="";

};

input.addEventListener("keypress",e=>{
if(e.key==="Enter") sendChatMsg();
});

}