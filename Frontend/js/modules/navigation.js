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

window.toggleMobileNav = function() {
  const mobileNav = document.getElementById("mobileNav");
  const hamburgerBtn = document.getElementById("hamburgerBtn");
  if (mobileNav) {
    const isHidden = mobileNav.hidden;
    mobileNav.hidden = !isHidden;
    if (hamburgerBtn) {
      hamburgerBtn.setAttribute("aria-expanded", !isHidden);
    }
  }
};

window.closeMobileNav = function() {
  const mobileNav = document.getElementById("mobileNav");
  const hamburgerBtn = document.getElementById("hamburgerBtn");
  if (mobileNav) {
    mobileNav.hidden = true;
    if (hamburgerBtn) {
      hamburgerBtn.setAttribute("aria-expanded", false);
    }
  }
};

}