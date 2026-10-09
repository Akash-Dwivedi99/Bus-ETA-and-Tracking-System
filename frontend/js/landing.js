(() => {
  const animation = document.getElementById('hero-bus-motion');
  if (!animation || typeof animation.beginElement !== 'function' || typeof animation.endElement !== 'function') return;
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const applyPreference = () => {
    if (reduceMotion.matches) animation.endElement();
    else animation.beginElement();
  };
  applyPreference();
  reduceMotion.addEventListener('change', applyPreference);
})();
