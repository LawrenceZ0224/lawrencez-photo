(() => {
  const gallery = document.querySelector('[data-film-gallery]');
  if (!gallery) return;
  const frames = [...gallery.querySelectorAll('[data-film-frame]')];
  const thumbs = [...gallery.querySelectorAll('[data-film-thumb]')];
  if (!frames.length) return;
  const previous = gallery.querySelector('[data-film-prev]');
  const next = gallery.querySelector('[data-film-next]');
  const count = gallery.querySelector('[data-film-count]');
  const status = gallery.querySelector('[data-film-status]');
  const retry = gallery.querySelector('[data-film-retry]');
  const strip = gallery.querySelector('.film-thumbnails');
  let current = 0, requested = 0, sequence = 0;
  const number = n => String(n).padStart(2, '0');

  const centerThumbnail = () => {
    const box = strip.getBoundingClientRect();
    const thumb = thumbs[current].getBoundingClientRect();
    if (thumb.left < box.left + 4 || thumb.right > box.right - 4) {
      strip.scrollTo({left: strip.scrollLeft + thumb.left - box.left - (box.width - thumb.width) / 2,
        behavior: 'auto'});
    }
  };

  async function show(index) {
    requested = (index + frames.length) % frames.length;
    const target = requested, version = ++sequence;
    retry.hidden = true;
    status.textContent = '';
    if (target === current) {
      gallery.removeAttribute('aria-busy');
      return;
    }
    gallery.setAttribute('aria-busy', 'true');
    const image = frames[target].querySelector('img');
    image.loading = 'eager';
    const waiting = setTimeout(() => {if (version === sequence) status.textContent = '照片加载中…';}, 500);
    try {
      await image.decode();
      if (version !== sequence) return;
      frames[current].hidden = true;
      frames[target].hidden = false;
      thumbs[current].setAttribute('aria-current', 'false');
      thumbs[target].setAttribute('aria-current', 'true');
      current = target;
      gallery.style.setProperty('--film-photo-ratio', Number(image.getAttribute('height')) / Number(image.getAttribute('width')));
      count.textContent = `${number(current + 1)} / ${number(frames.length)}`;
      status.textContent = '';
      centerThumbnail();
    } catch (_) {
      if (version !== sequence) return;
      status.textContent = '照片未能加载，请重试。';
      retry.hidden = false;
    } finally {
      clearTimeout(waiting);
      if (version === sequence) gallery.removeAttribute('aria-busy');
    }
  }

  previous.hidden = next.hidden = frames.length < 2;
  previous.addEventListener('click', () => show(requested - 1));
  next.addEventListener('click', () => show(requested + 1));
  thumbs.forEach((thumb, index) => thumb.addEventListener('click', () => show(index)));
  retry.addEventListener('click', () => {
    // Reassign the source so a previously failed request can be attempted again.
    const frame = frames[requested];
    frame.querySelectorAll('source').forEach(source => {source.srcset = source.srcset;});
    const image = frame.querySelector('img');
    image.src = image.src;
    show(requested);
  });
  gallery.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    const targets = {ArrowLeft: requested - 1, ArrowRight: requested + 1, Home: 0, End: frames.length - 1};
    if (!(event.key in targets)) return;
    event.preventDefault();
    show(targets[event.key]);
  });
  let start = null;
  const stage = gallery.querySelector('.film-stage');
  stage.addEventListener('touchstart', event => {
    start = event.touches.length === 1 ? {x: event.touches[0].clientX, y: event.touches[0].clientY} : null;
  }, {passive:true});
  stage.addEventListener('touchend', event => {
    if (!start || !event.changedTouches.length) return;
    const dx = event.changedTouches[0].clientX - start.x;
    const dy = event.changedTouches[0].clientY - start.y;
    start = null;
    if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.5) show(requested + (dx < 0 ? 1 : -1));
  }, {passive:true});
  stage.addEventListener('touchcancel', () => {start = null;}, {passive:true});
})();
