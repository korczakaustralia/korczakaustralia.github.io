/* Janusz Korczak Association Australia - site behaviour
   Replaces the AMP components the Mobirise export depended on:
   off-canvas menu, accordion, image slider, image viewer, contact form. */
(function () {
  'use strict';

  /* ---------------------------------------------------------------- off-canvas menu */
  var sidebar = document.getElementById('sidebar');
  if (sidebar) {
    var mask = document.createElement('div');
    mask.className = 'amp-sidebar-mask';
    document.body.appendChild(mask);

    var setSidebar = function (open) {
      sidebar.classList.toggle('is-open', open);
      mask.classList.toggle('is-open', open);
      sidebar.setAttribute('aria-hidden', open ? 'false' : 'true');
    };
    document.querySelectorAll('[data-sidebar]').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        setSidebar(btn.getAttribute('data-sidebar') === 'toggle' ? !sidebar.classList.contains('is-open') : false);
      });
    });
    mask.addEventListener('click', function () { setSidebar(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setSidebar(false); });
    sidebar.querySelectorAll('a[href]').forEach(function (a) {
      a.addEventListener('click', function () { setSidebar(false); });
    });
  }

  /* ---------------------------------------------------------------- accordion */
  document.querySelectorAll('[data-accordion]').forEach(function (title) {
    var body = document.querySelector(title.getAttribute('data-accordion'));
    if (!body) return;
    var group = title.closest('.amp-accordion') || document;
    var toggle = function (e) {
      e.preventDefault();
      var wasOpen = !body.hidden;
      group.querySelectorAll('.accordion-item-body').forEach(function (b) { b.hidden = true; });
      body.hidden = wasOpen;
    };
    title.addEventListener('click', toggle);
    title.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') toggle(e); });
  });

  /* ---------------------------------------------------------------- slider */
  document.querySelectorAll('[data-carousel]').forEach(function (car) {
    var track = car.querySelector('.amp-carousel-track');
    var slides = track.children.length;
    var index = 0, timer = null;
    var loop = car.hasAttribute('data-loop');
    var delay = parseInt(car.getAttribute('data-autoplay'), 10);

    var go = function (i) {
      if (loop) i = (i + slides) % slides; else i = Math.max(0, Math.min(slides - 1, i));
      index = i;
      track.style.transform = 'translateX(' + (-100 * index) + '%)';
    };
    var start = function () {
      if (!delay || slides < 2) return;
      stop();
      timer = setInterval(function () { go(index + 1); }, delay);
    };
    var stop = function () { if (timer) { clearInterval(timer); timer = null; } };

    var prev = car.querySelector('[data-carousel-prev]');
    var next = car.querySelector('[data-carousel-next]');
    var handle = function (delta) {
      return function (e) {
        e.preventDefault(); e.stopPropagation();
        go(index + delta); start();
      };
    };
    if (prev) prev.addEventListener('click', handle(-1));
    if (next) next.addEventListener('click', handle(1));
    [prev, next].forEach(function (b) {
      if (b) b.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') b.click(); });
    });
    car.addEventListener('mouseenter', stop);
    car.addEventListener('mouseleave', start);

    // swipe support
    var startX = null;
    car.addEventListener('touchstart', function (e) { startX = e.touches[0].clientX; stop(); }, { passive: true });
    car.addEventListener('touchend', function (e) {
      if (startX === null) return;
      var dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 40) go(index + (dx < 0 ? 1 : -1));
      startX = null; start();
    });
    go(0); start();
  });

  /* ---------------------------------------------------------------- image viewer */
  var lightbox = document.getElementById('image-lightbox');
  if (lightbox) {
    var lbImg = lightbox.querySelector('img');
    var open = function (src, alt) {
      lbImg.src = src; lbImg.alt = alt || '';
      lightbox.hidden = false;
      document.documentElement.classList.add('overflow-hidden');
    };
    var close = function () {
      lightbox.hidden = true;
      document.documentElement.classList.remove('overflow-hidden');
    };
    document.querySelectorAll('[data-lightbox]').forEach(function (el) {
      var img = el.tagName === 'IMG' ? el : el.querySelector('img');
      if (!img) return;
      var trigger = function (e) { e.preventDefault(); open(img.currentSrc || img.src, img.alt); };
      el.addEventListener('click', trigger);
      el.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') trigger(e); });
    });
    lightbox.addEventListener('click', function (e) { e.preventDefault(); close(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !lightbox.hidden) close(); });
  }

  /* ---------------------------------------------------------------- contact form (Formoid) */
  document.querySelectorAll('form[data-form]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var ok = form.querySelector('[data-form-success]');
      var bad = form.querySelector('[data-form-error]');
      if (ok) ok.hidden = true;
      if (bad) bad.hidden = true;
      var body = new URLSearchParams(new FormData(form));
      body.append('form[title]', form.getAttribute('data-form-title') || '');
      fetch(form.action, { method: 'POST', body: body, mode: 'cors' })
        .then(function (r) {
          if (!r.ok) throw new Error(r.statusText);
          form.reset();
          if (ok) ok.hidden = false;
        })
        .catch(function (err) {
          if (bad) { bad.textContent = 'Failed! ' + (err && err.message ? err.message : ''); bad.hidden = false; }
        });
    });
  });
})();
