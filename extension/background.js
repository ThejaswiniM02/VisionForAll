chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "applyFilter" && message.filterType && sender.tab) {
    chrome.scripting.executeScript({
      target: { tabId: sender.tab.id },
      func: (filterType) => {
        // Remove existing filter
        const existing = document.getElementById('cvd-filter');
        if (existing) existing.remove();

        if (filterType === 'normal') {
          document.body.style.filter = "";
          return;
        }

        const svgNS = "http://www.w3.org/2000/svg";
        const svg = document.createElementNS(svgNS, 'svg');
        svg.style.position = 'absolute';
        svg.style.width = '0';
        svg.style.height = '0';
        svg.style.overflow = 'hidden';
        svg.id = 'cvd-filter';

        // Define filters inside the function:
        const filters = {
          protanopia: `
            <filter id="protanopia">
              <feColorMatrix type="matrix" values="0.567 0.433 0 0 0 0.558 0.442 0 0 0 0 0.242 0.758 0 0 0 0 0 1 0"/>
            </filter>`,
          deuteranopia: `
            <filter id="deuteranopia">
              <feColorMatrix type="matrix" values="0.625 0.375 0 0 0 0.7 0.3 0 0 0 0 0.3 0.7 0 0 0 0 0 1 0"/>
            </filter>`,
          tritanopia: `
            <filter id="tritanopia">
              <feColorMatrix type="matrix" values="0.95 0.05 0 0 0 0 0.433 0.567 0 0 0 0.475 0.525 0 0 0 0 0 1 0"/>
            </filter>`
        };
chrome.runtime.onInstalled.addListener(() => {
  console.log("Extension installed.");
});

        svg.innerHTML = filters[filterType];
        document.body.appendChild(svg);
        document.body.style.filter = `url(#${filterType})`;
      },
      args: [message.filterType]
    });
  }
});
