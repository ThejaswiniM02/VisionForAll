function applyCVDFilter(type = "protanopia") {
  // Remove existing filter element if present
  const existing = document.getElementById('cvd-filter');
  if (existing) existing.remove();

  if (type === 'normal') {
    document.body.style.filter = "";
    return;
  }

  fetch(chrome.runtime.getURL(`filters/${type}.svg`))
    .then(response => response.text())
    .then(svgText => {
      const div = document.createElement('div');
      div.style.position = 'absolute';
      div.style.width = 0;
      div.style.height = 0;
      div.style.overflow = 'hidden';
      div.id = 'cvd-filter';
      div.innerHTML = svgText;

      document.body.appendChild(div);
      document.body.style.filter = `url(#${type})`;
    })
    .catch(err => console.error('Failed to load filter SVG:', err));
}
