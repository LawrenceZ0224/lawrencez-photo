(() => {
  const icon = path => `<svg viewBox="0 0 32 32" aria-hidden="true"><path d="${path}"/></svg>`;
  const mobile = window.matchMedia('(max-width: 700px)');
  const navigation = document.querySelector('#site-navigation');
  const menuToggle = document.querySelector('.menu-toggle');
  if (navigation && menuToggle && typeof HTMLDialogElement !== 'undefined') {
    const header = menuToggle.closest('header');
    const menu = document.createElement('dialog');
    menu.id = 'mobile-navigation';
    menu.className = 'mobile-navigation';
    menu.setAttribute('aria-label', '主要导航');
    menu.innerHTML = `<button type="button" class="menu-close" aria-label="关闭导航" autofocus>${icon('M6 6L26 26M26 6L6 26')}</button>`;
    document.body.append(menu);
    let scrollPosition = 0, scrollLocked = false;
    const resetLocations = () => navigation.querySelectorAll('.nav-group').forEach(group => {
      group.classList.remove('open');
      group.querySelector('.nav-trigger').setAttribute('aria-expanded', 'false');
    });
    const restorePage = () => {
      if (!scrollLocked) return;
      scrollLocked = false;
      document.body.classList.remove('menu-open');
      document.body.style.removeProperty('--menu-scroll-offset');
      window.scrollTo({top: scrollPosition, behavior: 'instant'});
      menuToggle.setAttribute('aria-expanded', 'false');
      resetLocations();
      if (mobile.matches) menuToggle.focus({preventScroll: true});
    };
    const closeMenu = () => {
      if (!menu.open) return;
      menu.close();
      restorePage();
    };
    const syncViewport = () => {
      closeMenu();
      resetLocations();
      // The same navigation moves between the desktop header and mobile dialog.
      (mobile.matches ? menu : header).append(navigation);
      menuToggle.hidden = !mobile.matches;
      header.classList.toggle('mobile-menu-ready', mobile.matches);
    };
    menuToggle.addEventListener('click', () => {
      if (!mobile.matches || menu.open) return;
      scrollPosition = window.scrollY;
      scrollLocked = true;
      document.body.style.setProperty('--menu-scroll-offset', `-${scrollPosition}px`);
      document.body.classList.add('menu-open');
      menu.showModal();
      menu.scrollTop = 0;
      menuToggle.setAttribute('aria-expanded', 'true');
    });
    menu.querySelector('.menu-close').addEventListener('click', closeMenu);
    menu.addEventListener('close', () => { if (!menu.open) restorePage(); });
    menu.addEventListener('cancel', event => { event.preventDefault(); closeMenu(); });
    menu.addEventListener('keydown', event => {
      if (event.key !== 'Tab') return;
      const items = [...menu.querySelectorAll('a, button')].filter(item => item.getClientRects().length);
      const first = items[0], last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault(); last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault(); first.focus();
      }
    });
    navigation.addEventListener('click', event => {
      if (event.target.closest('a') && !event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey) closeMenu();
    });
    window.addEventListener('pagehide', closeMenu);
    mobile.addEventListener('change', syncViewport);
    syncViewport();
  }
  document.querySelectorAll('.nav-group').forEach(group => {
    const trigger = group.querySelector('.nav-trigger');
    const setOpen = open => { group.classList.toggle('open', open); trigger.setAttribute('aria-expanded', String(open)); };
    group.addEventListener('pointerenter', event => { if (event.pointerType === 'mouse' && !mobile.matches) setOpen(true); });
    group.addEventListener('pointerleave', event => { if (event.pointerType === 'mouse' && !mobile.matches && !group.contains(document.activeElement)) setOpen(false); });
    trigger.addEventListener('click', () => setOpen(!group.classList.contains('open')));
    group.addEventListener('focusout', event => { if (!group.contains(event.relatedTarget)) setOpen(false); });
    document.addEventListener('click', event => { if (!group.contains(event.target)) setOpen(false); });
    group.addEventListener('keydown', event => {
      if (event.key === 'Escape' && group.classList.contains('open')) {
        event.preventDefault(); event.stopPropagation(); setOpen(false); trigger.focus();
      }
      if (event.key === 'ArrowDown' && event.target === trigger) {
        event.preventDefault(); setOpen(true); group.querySelector('.nav-menu a')?.focus();
      }
    });
  });
  const links = [...document.querySelectorAll('[data-photo]')];
  if (!links.length || typeof HTMLDialogElement === 'undefined') return;
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
