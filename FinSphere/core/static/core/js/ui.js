// 3D tilt effect for .tilt cards
document.querySelectorAll('.tilt').forEach(el => {
  el.addEventListener('pointermove', e => {
    const r = el.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
    el.style.transform = `perspective(800px) rotateY(${x * 10}deg) rotateX(${-y * 10}deg) translateZ(6px)`;
  });
  el.addEventListener('pointerleave', () => el.style.transform = '');
});
