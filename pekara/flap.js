(function () {
  const init = () => {
    const boards = document.querySelectorAll('[data-flap-to]');
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    boards.forEach((board) => {
      const from = board.dataset.flapFrom || board.dataset.flapTo;
      const to = board.dataset.flapTo;
      const cells = [];
      board.replaceChildren();

      [...to].forEach((character, index) => {
        const cell = document.createElement('span');
        cell.className = 'flap__cell';
        if (character === ':') {
          cell.classList.add('flap__separator');
          cell.textContent = ':';
          board.append(cell);
          return;
        }

        const start = from[index] || character;
        cell.innerHTML = '<span class="flap__top"><i></i></span><span class="flap__bottom"><i></i></span><span class="flap__top flap__moving-top"><i></i></span><span class="flap__bottom flap__moving-bottom"><i></i></span>';
        cell.dataset.current = start;
        cell.dataset.target = character;
        cell.querySelectorAll('i').forEach((glyph) => { glyph.textContent = start; });
        board.append(cell);
        cells.push(cell);
      });

      const finish = () => cells.forEach((cell) => {
        const target = cell.dataset.target;
        cell.dataset.current = target;
        cell.classList.remove('is-flipping');
        cell.querySelectorAll('i').forEach((glyph) => {
          glyph.textContent = target;
        });
      });

      if (reducedMotion || !('IntersectionObserver' in window)) {
        finish();
        return;
      }

      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting || entry.intersectionRatio < 0.4) return;
          observer.unobserve(board);
          cells.forEach((cell, index) => {
            const delay = index * 80;
            const advance = () => {
              const current = Number(cell.dataset.current);
              const target = Number(cell.dataset.target);
              if (current >= target) return;
              const next = String(current + 1);
              cell.querySelector('.flap__moving-top i').textContent = String(current);
              cell.querySelector('.flap__moving-bottom i').textContent = next;
              // wie bei der echten Tafel: hinter der fallenden Klappe steht oben schon die neue Ziffer
              cell.querySelector('.flap__top:not(.flap__moving-top) i').textContent = next;
              cell.classList.add('is-flipping');
              window.setTimeout(() => {
                cell.dataset.current = next;
                cell.classList.remove('is-flipping');
                cell.querySelectorAll('i').forEach((glyph) => { glyph.textContent = next; });
                if (Number(next) < target) window.setTimeout(advance, 0);
              }, 140);
            };
            window.setTimeout(advance, delay);
          });
        });
      }, { threshold: 0.4 });
      observer.observe(board);
    });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
