console.log("Content script injected");

function applyCVDFilter(type = "protanopia") {
  // Remove existing filter element if present
  const existing = document.getElementById('cvd-filter');
  if (existing) existing.remove();

  if (type === 'normal') {
    // Clear filter
    document.body.style.filter = "";
    console.log("Filter cleared (normal mode)");
    return;
  }

  // Load SVG filter and apply
  fetch(chrome.runtime.getURL(`filters/${type}.svg`))
    .then(response => {
      if (!response.ok) {
        throw new Error(`Failed to fetch filter SVG: ${response.status}`);
      }
      return response.text();
    })
    .then(svgText => {
      const div = document.createElement('div');
      div.style.position = 'absolute';
      div.style.width = '0';
      div.style.height = '0';
      div.style.overflow = 'hidden';
      div.id = 'cvd-filter';
      div.innerHTML = svgText;

      document.body.appendChild(div);
      document.body.style.filter = `url(#${type})`;

      console.log(`Applied filter: ${type}`);
    })
    .catch(err => console.error('Failed to load filter SVG:', err));
}

// Listen for messages from popup.js
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log("Message received in content script:", message);  // Add this line
  if (message.type === "SET_CVD_FILTER") {
    applyCVDFilter(message.mode);
    sendResponse({ status: "Filter applied" });
  }
});
