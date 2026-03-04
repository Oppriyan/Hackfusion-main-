export function initNavigation() {

window.goTo = function(page) {

  document.querySelectorAll('.page').forEach(p =>
    p.classList.remove('active')
  );

  document
    .getElementById('page-' + page)
    ?.classList.add('active');

  window.scrollTo(0,0);

};

}