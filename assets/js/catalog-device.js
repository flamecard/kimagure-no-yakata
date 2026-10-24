(() => {
  const script = document.currentScript;
  const current = new URL(window.location.href);
  const catalog = new URL(script.dataset.catalog, current);
  const requested = current.searchParams.get('view');
  const mobile = /iPhone|iPod|Android|Windows Phone|Mobile/i.test(navigator.userAgent)
    || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  const view = requested === 'pc' || requested === 'mobile' ? requested : (mobile ? 'mobile' : 'pc');
  const target = new URL(view === 'mobile' ? 'mobile/' : './', catalog);
  const currentPath = current.pathname.replace(/index\.html$/, '');
  if (currentPath !== target.pathname) {
    target.search = current.search;
    target.hash = current.hash;
    window.location.replace(target.href);
  }
})();
