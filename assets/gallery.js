(() => {
  const links = [...document.querySelectorAll('[data-photo]')];
  if (!links.length || typeof HTMLDialogElement === 'undefined') return;
  const dialog = document.createElement('dialog');
  dialog.className = 'viewer';
  dialog.setAttribute('aria-label', '查看完整照片');
  dialog.innerHTML = '<div class="viewer-bar"><span class="viewer-count" aria-live="polite"></span><button type="button" class="viewer-close" autofocus>关闭</button></div><img class="viewer-image" alt=""><div class="viewer-bottom"><button type="button" class="viewer-prev">上一张</button><span class="viewer-caption" aria-live="polite"></span><button type="button" class="viewer-next">下一张</button></div>';
  document.body.append(dialog);
  let index = 0, origin = null, startX = null, startY = null;
  const img = dialog.querySelector('img');
  function show(next) {
    index = Math.max(0, Math.min(next, links.length - 1));
    const link = links[index];
    img.src = link.href;
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
    if(event.touches.length !== 1) { startX = null; return; }
    startX = event.touches[0].clientX; startY = event.touches[0].clientY;
  }, {passive:true});
  img.addEventListener('touchend', event => {
    if(startX === null) return;
    const dx = event.changedTouches[0].clientX - startX;
    const dy = event.changedTouches[0].clientY - startY;
    if(Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy)) show(index + (dx < 0 ? 1 : -1));
    startX = null;
  }, {passive:true});
})();
