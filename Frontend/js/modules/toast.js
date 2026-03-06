export function initToast(){

window.toast = function(msg,type='blue'){

  const wrap = document.getElementById('toastWrap');

  const t = document.createElement('div');

  t.className = 'toast ' + type;

  t.innerText = msg;

  wrap.appendChild(t);

  setTimeout(()=>{
    t.remove();
  },3500);

};

}