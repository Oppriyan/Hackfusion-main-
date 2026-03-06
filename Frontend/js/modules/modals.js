export function initModals(){

window.openModal = function(id){

  const el = document.getElementById(id);

  el?.classList.add("show");

  document.body.style.overflow="hidden";

};

window.closeModal = function(id){

  const el = document.getElementById(id);

  el?.classList.remove("show");

  document.body.style.overflow="";

};

}