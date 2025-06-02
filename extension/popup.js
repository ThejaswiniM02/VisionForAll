const protanopiaToggle = document.getElementById('protanopia-toggle');
const deuteranopiaToggle = document.getElementById('deuteranopia-toggle');
const tritanopiaToggle = document.getElementById('tritanopia-toggle');

const toggles = [protanopiaToggle, deuteranopiaToggle, tritanopiaToggle];

toggles.forEach(toggle => {
  toggle.addEventListener('change', () => {
    if (toggle.checked) {
      toggles.forEach(t => { if (t !== toggle) t.checked = false; });
      applyFilter(toggle.id.replace('-toggle', ''));
    } else {
      applyFilter('normal');
    }
  });
});

function applyFilter(type) {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.scripting.executeScript({
      target: { tabId: tabs[0].id },
      func: (filterType) => {
        const existing = document.getElementById('cvd-filter');
        if (existing) existing.remove();

        if (filterType === 'normal') {
          document.body.style.filter = '';
          return;
        }

        const filters = {
          protanopia: `
            <filter id="protanopia">
              <feColorMatrix type="matrix" values="0.567,0.433,0,0,0 0.558,0.442,0,0,0 0,0.242,0.758,0,0 0,0,0,1,0"/>
            </filter>`,
          deuteranopia: `
            <filter id="deuteranopia">
              <feColorMatrix type="matrix" values="0.625,0.375,0,0,0 0.7,0.3,0,0,0 0,0.3,0.7,0,0 0,0,0,1,0"/>
            </filter>`,
          tritanopia: `
            <filter id="tritanopia">
              <feColorMatrix type="matrix" values="0.95,0.05,0,0,0 0,0.433,0.567,0,0 0,0.475,0.525,0,0 0,0,0,1,0"/>
            </filter>`
        };

        const svgNS = 'http://www.w3.org/2000/svg';
        const svgElem = document.createElementNS(svgNS, 'svg');
        svgElem.style.position = 'absolute';
        svgElem.style.width = '0';
        svgElem.style.height = '0';
        svgElem.style.overflow = 'hidden';
        svgElem.id = 'cvd-filter';
        svgElem.innerHTML = filters[filterType];
        document.body.appendChild(svgElem);

        document.body.style.filter = `url(#${filterType})`;
      },
      args: [type]
    });
  });
}
