(function () {
  const root = document.querySelector('[data-it-ads-carousel]');
  if (!root) return;

  const track = root.querySelector('[data-carousel-track]');
  const viewport = root.querySelector('[data-carousel-viewport]');
  const prevBtn = root.querySelector('[data-carousel-prev]');
  const nextBtn = root.querySelector('[data-carousel-next]');
  const dotsHost = root.querySelector('[data-carousel-dots]');
  const slides = Array.from(root.querySelectorAll('.it-ads-carousel-slide'));

  if (!track || !viewport || slides.length === 0) return;

  let index = slides.findIndex((slide) => slide.classList.contains('is-active'));
  if (index < 0) index = 0;

  const dotButtons = slides.map((_, slideIndex) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'it-ads-carousel-dot';
    button.setAttribute('role', 'tab');
    button.setAttribute('aria-label', `Schermata ${slideIndex + 1} di ${slides.length}`);
    button.addEventListener('click', () => goTo(slideIndex));
    dotsHost.appendChild(button);
    return button;
  });

  const update = () => {
    slides.forEach((slide, slideIndex) => {
      const isActive = slideIndex === index;
      slide.classList.toggle('is-active', isActive);
      slide.setAttribute('aria-hidden', isActive ? 'false' : 'true');
    });

    dotButtons.forEach((button, slideIndex) => {
      const isActive = slideIndex === index;
      button.classList.toggle('is-active', isActive);
      button.setAttribute('aria-selected', isActive ? 'true' : 'false');
      button.tabIndex = isActive ? 0 : -1;
    });

    if (prevBtn) prevBtn.disabled = index === 0;
    if (nextBtn) nextBtn.disabled = index === slides.length - 1;

    const activeSlide = slides[index];
    const maxOffset = Math.max(0, track.scrollWidth - viewport.clientWidth);
    const slideCenter = activeSlide.offsetLeft + activeSlide.offsetWidth / 2;
    const offset = Math.min(Math.max(0, slideCenter - viewport.clientWidth / 2), maxOffset);
    track.style.transform = `translateX(${-offset}px)`;
  };

  const goTo = (nextIndex) => {
    index = Math.max(0, Math.min(slides.length - 1, nextIndex));
    update();
  };

  if (prevBtn) {
    prevBtn.addEventListener('click', () => goTo(index - 1));
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', () => goTo(index + 1));
  }

  viewport.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') {
      event.preventDefault();
      goTo(index - 1);
    } else if (event.key === 'ArrowRight') {
      event.preventDefault();
      goTo(index + 1);
    }
  });

  let touchStartX = 0;
  let touchDeltaX = 0;

  viewport.addEventListener('touchstart', (event) => {
    touchStartX = event.changedTouches[0].screenX;
    touchDeltaX = 0;
  }, { passive: true });

  viewport.addEventListener('touchmove', (event) => {
    touchDeltaX = event.changedTouches[0].screenX - touchStartX;
  }, { passive: true });

  viewport.addEventListener('touchend', () => {
    if (Math.abs(touchDeltaX) < 40) return;
    if (touchDeltaX < 0) goTo(index + 1);
    else goTo(index - 1);
  }, { passive: true });

  window.addEventListener('resize', update);
  update();
})();
