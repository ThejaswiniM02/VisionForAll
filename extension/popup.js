document.addEventListener("DOMContentLoaded", () => {
  const toggleModes = document.getElementById("toggleModes");
  const toggleIcon = document.getElementById("toggleIcon");
  const modeButtons = document.getElementById("mode-buttons");
  const simulationBtn = document.getElementById("simulation-btn");
  const correctionBtn = document.getElementById("correction-btn");
  const toggleContainer = document.getElementById("toggleContainer");

  let isDropdownVisible = false;

  function sendFilterRequest(mode) {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (!tabs[0]?.id) return;
      const tabId = tabs[0].id;

      // Inject the content script manually
      chrome.scripting.executeScript(
        {
          target: { tabId: tabId },
          files: ["content.js"]
        },
        () => {
          if (chrome.runtime.lastError) {
            console.error("Injection failed:", chrome.runtime.lastError.message);
          } else {
            console.log("Content script injected from popup");

            // Now send the message
            chrome.tabs.sendMessage(tabId, { type: "SET_CVD_FILTER", mode }, (response) => {
              if (chrome.runtime.lastError) {
                console.error("Message sending failed:", chrome.runtime.lastError.message);
              } else {
                console.log(response?.status);
              }
            });
          }
        }
      );
    });
  }

  if (toggleModes && toggleIcon && modeButtons) {
    toggleModes.addEventListener("click", () => {
      isDropdownVisible = !isDropdownVisible;
      modeButtons.style.display = isDropdownVisible ? "flex" : "none";
      toggleIcon.innerHTML = isDropdownVisible ? "&#9650;" : "&#9660;";
    });
  }

  if (simulationBtn && toggleContainer && modeButtons && toggleIcon) {
    simulationBtn.addEventListener("click", () => {
      toggleContainer.style.display = "block";
      modeButtons.style.display = "none";
      toggleIcon.innerHTML = "&#9660;";
      isDropdownVisible = false;
    });
  }

  if (correctionBtn && toggleContainer && modeButtons && toggleIcon) {
    correctionBtn.addEventListener("click", () => {
      // Uncheck simulation mode checkboxes
      document.getElementById("protanopia-toggle").checked = false;
      document.getElementById("deuteranopia-toggle").checked = false;
      document.getElementById("tritanopia-toggle").checked = false;

      toggleContainer.style.display = "none";
      modeButtons.style.display = "none";
      toggleIcon.innerHTML = "&#9660;";
      isDropdownVisible = false;

      // Example correction mode (can be customized)
      sendCorrectionRequest("protanopia");
      sendCorrectionRequest("deuteranopia");
      sendCorrectionRequest("tritanopia");
    });
  }

  const simulationToggles = [
    document.getElementById("protanopia-toggle"),
    document.getElementById("deuteranopia-toggle"),
    document.getElementById("tritanopia-toggle")
  ];

  simulationToggles.forEach((toggle, idx) => {
    if (!toggle) return;

    toggle.addEventListener("change", () => {
      if (toggle.checked) {
        // Uncheck others
        simulationToggles.forEach((otherToggle, otherIdx) => {
          if (otherIdx !== idx) {
            otherToggle.checked = false;
          }
        });
        const mode = toggle.id.split("-")[0]; // extract "protanopia", "deuteranopia", etc.
        sendFilterRequest(mode);
      } else {
        sendFilterRequest("normal");
      }
    });
  });

  // Optional initial debug script injection (can be removed if not needed)
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (!tabs[0]?.id) return;
    chrome.scripting.executeScript({
      target: { tabId: tabs[0].id },
      func: () => {
        console.log("Hello from injected script via scripting API!");
      }
    });
  });
});
