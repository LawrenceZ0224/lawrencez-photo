(() => {
  const root = document.querySelector('[data-portrait-carousel]');
  if (!root) return;
  const slides = [...root.querySelectorAll('[data-slide]')];
  if (!slides.length) return;
  const slideshow = root.hasAttribute('data-slideshow');
  const previous = root.querySelector('[data-prev]');
  const next = root.querySelector('[data-next]');
  const play = root.querySelector('[data-play]');
  const count = root.querySelector('[data-count]') || document.querySelector('[data-collection-count]');
  const status = root.querySelector('.portrait-status');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const menu = document.querySelector('#mobile-navigation');
  let index = 0, requested = 0, revision = 0, timer = null;
  let playing = slideshow && slides.length > 1 && !motion.matches;
  let ready = false;

  previous.hidden = next.hidden = slides.length < 2;
  if (play) play.hidden = slides.length < 2;
  if (count) count.hidden = !slideshow && slides.length < 2;

  function playbackUI() {
    if (play) {
      play.textContent = playing ? 'Pause' : 'Play';
      play.setAttribute('aria-label', playing ? '暂停自动播放' : '开始自动播放');
    }
    if (count) count.setAttribute('aria-live', playing ? 'off' : 'polite');
  }
  function stop() {
    playing = false;
    clearTimeout(timer);
    playbackUI();
  }
  function schedule() {
    clearTimeout(timer);
    if (playing && ready && !document.hidden && !menu?.open) {
      timer = setTimeout(() => show(index + 1), 4500);
    }
  }
  function updateCount() {
    if (count) count.textContent = `${String(index + 1).padStart(2, '0')} / ${String(slides.length).padStart(2, '0')}`;
  }
  function warmNext() {
    if (slides.length > 1) slides[(index + 1) % slides.length].querySelector('img').loading = 'eager';
  }
  async function load(slide) {
    const img = slide.querySelector('img');
    img.loading = 'eager';
    // Reassign a failed request so the next arrow press can retry after a network interruption.
    if (img.complete && !img.naturalWidth) img.src = img.src;
    await img.decode();
  }
  async function show(position, manual = false) {
    if (manual) stop();
    clearTimeout(timer);
    requested = (position + slides.length) % slides.length;
    const target = requested, version = ++revision;
    root.setAttribute('aria-busy', 'true');
    status.textContent = '';
    try {
      await load(slides[target]);
      if (version !== revision) return;
      // Keep the previous picture visible until the next one has decoded.
      slides.forEach((slide, n) => { slide.hidden = n !== target; });
      index = target;
      ready = true;
      updateCount();
      warmNext();
      schedule();
    } catch {
      if (version !== revision) return;
      stop();
      requested = index;
      status.textContent = '照片加载失败，请重试或刷新页面。';
    } finally {
      if (version === revision) root.removeAttribute('aria-busy');
    }
  }

  previous.addEventListener('click', () => show(requested - 1, true));
  next.addEventListener('click', () => show(requested + 1, true));
  play?.addEventListener('click', () => {
    playing = !playing;
    playbackUI();
    schedule();
  });
  root.addEventListener('focusin', event => {
    // Keyboard users can inspect controls without the displayed photo moving on.
    if (event.target !== play) stop();
  });
  document.addEventListener('keydown', event => {
    if (menu?.open || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    if (event.target.closest('input, textarea, select, [contenteditable="true"]')) return;
    if (event.key === 'ArrowLeft') { event.preventDefault(); show(requested - 1, true); }
    if (event.key === 'ArrowRight') { event.preventDefault(); show(requested + 1, true); }
  });
  let touch = null;
  root.addEventListener('touchstart', event => {
    touch = event.touches.length === 1 ? {x: event.touches[0].clientX, y: event.touches[0].clientY} : null;
  }, {passive: true});
  root.addEventListener('touchend', event => {
    if (!touch || !event.changedTouches.length) return;
    const dx = event.changedTouches[0].clientX - touch.x;
    const dy = event.changedTouches[0].clientY - touch.y;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.3) show(requested + (dx < 0 ? 1 : -1), true);
    touch = null;
  }, {passive: true});
  root.addEventListener('touchcancel', () => { touch = null; }, {passive: true});
  document.addEventListener('visibilitychange', () => {
    clearTimeout(timer);
    if (!document.hidden) schedule();
  });
  if (menu) new MutationObserver(() => { if (menu.open) stop(); }).observe(menu, {attributes: true, attributeFilter: ['open']});
  motion.addEventListener('change', () => { if (motion.matches) stop(); });
  window.addEventListener('pagehide', () => clearTimeout(timer));
  window.addEventListener('pageshow', schedule);
  playbackUI();
  updateCount();
  show(0);
})();
