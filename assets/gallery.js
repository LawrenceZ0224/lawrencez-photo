(() => {
  document.querySelectorAll('.nav-group').forEach(group => {
    const trigger = group.querySelector('.nav-trigger');
    const setOpen = open => { group.classList.toggle('open', open); trigger.setAttribute('aria-expanded', String(open)); };
    group.addEventListener('pointerenter', event => { if (event.pointerType === 'mouse') setOpen(true); });
    group.addEventListener('pointerleave', event => { if (event.pointerType === 'mouse' && !group.contains(document.activeElement)) setOpen(false); });
    trigger.addEventListener('click', () => setOpen(!group.classList.contains('open')));
    group.addEventListener('focusout', event => { if (!group.contains(event.relatedTarget)) setOpen(false); });
    document.addEventListener('click', event => { if (!group.contains(event.target)) setOpen(false); });
    group.addEventListener('keydown', event => {
      if (event.key === 'Escape') { setOpen(false); trigger.focus(); }
      if (event.key === 'ArrowDown' && event.target === trigger) {
        event.preventDefault(); setOpen(true); group.querySelector('.nav-menu a')?.focus();
      }
    });
  });
  const links = [...document.querySelectorAll('[data-photo]')];
  if (!links.length || typeof HTMLDialogElement === 'undefined') return;
  const icon = path => `<svg viewBox="0 0 32 32" aria-hidden="true"><path d="${path}"/></svg>`;
  const dialog = document.createElement('dialog');
  dialog.className = 'viewer';
  dialog.setAttribute('aria-label', '查看高清完整照片');
  dialog.innerHTML = `<button type="button" class="viewer-close" aria-label="关闭大图" title="关闭（Esc）" autofocus>${icon('M6 6L26 26M26 6L6 26')}</button><button type="button" class="viewer-prev" aria-label="上一张" title="上一张（←）">${icon('M21 5L10 16L21 27')}</button><img class="viewer-image" alt=""><button type="button" class="viewer-next" aria-label="下一张" title="下一张（→）">${icon('M11 5L22 16L11 27')}</button><span class="viewer-count" aria-live="polite"></span><span class="viewer-caption" aria-live="polite"></span>`;
  document.body.append(dialog);
  let index = 0, origin = null, startX = null, startY = null;
  const img = dialog.querySelector('img');
  img.onload = () => { img.style.opacity = '1'; };
  img.onerror = () => { img.style.opacity = '1'; dialog.querySelector('.viewer-caption').textContent = '图片加载失败，请关闭后重试。'; };
  function show(next) {
    index = Math.max(0, Math.min(next, links.length - 1));
    const link = links[index];
    if (img.src !== link.href) { img.style.opacity = '0'; img.src = link.href; }
    img.alt = link.dataset.caption;
    dialog.querySelector('.viewer-caption').textContent = link.dataset.caption;
    dialog.querySelector('.viewer-count').textContent = `${index + 1} / ${links.length}`;
    dialog.querySelector('.viewer-prev').disabled = index === 0;
    dialog.querySelector('.viewer-next').disabled = index === links.length - 1;
  }
  links.forEach((link, n) => link.addEventListener('click', event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault(); origin = link; show(n);
    dialog.showModal(); document.body.classList.add('viewing');
  }));
  dialog.querySelector('.viewer-close').onclick = () => dialog.close();
  dialog.querySelector('.viewer-prev').onclick = () => show(index - 1);
  dialog.querySelector('.viewer-next').onclick = () => show(index + 1);
  dialog.addEventListener('close', () => {
    document.body.classList.remove('viewing');
    if (origin) origin.focus({preventScroll:true});
  });
  dialog.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft') { event.preventDefault(); show(index - 1); }
    if (event.key === 'ArrowRight') { event.preventDefault(); show(index + 1); }
  });
  img.addEventListener('touchstart', event => {
    if (event.touches.length !== 1) { startX = null; return; }
    startX = event.touches[0].clientX; startY = event.touches[0].clientY;
  }, {passive:true});
  img.addEventListener('touchend', event => {
    if (startX === null) return;
    const dx = event.changedTouches[0].clientX - startX;
    const dy = event.changedTouches[0].clientY - startY;
    if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy)) show(index + (dx < 0 ? 1 : -1));
    startX = null;
  }, {passive:true});
})();
