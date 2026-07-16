// --------------------------------------------------
// Mobile Navigation
// --------------------------------------------------

function setMobileMenuState(menu, button, open) {
  if (!menu || !button) {
    return;
  }

  menu.classList.toggle("hidden", !open);
  button.setAttribute("aria-expanded", open ? "true" : "false");
}

function toggleMenu() {
  const menu = document.getElementById("mobileMenu");
  const button = document.getElementById("mobileMenuButton");

  if (!menu || !button) {
    return;
  }

  setMobileMenuState(menu, button, menu.classList.contains("hidden"));
}

document.addEventListener("DOMContentLoaded", function () {
  const menu = document.getElementById("mobileMenu");
  const button = document.getElementById("mobileMenuButton");

  if (!menu || !button) {
    return;
  }

  button.addEventListener("click", toggleMenu);

  menu.querySelectorAll("a").forEach(function (link) {
    link.addEventListener("click", function () {
      setMobileMenuState(menu, button, false);
    });
  });

  window.addEventListener("resize", function () {
    if (window.innerWidth >= 768) {
      setMobileMenuState(menu, button, false);
    }
  });
});


// --------------------------------------------------
// Search Modal
// --------------------------------------------------

function openSearch() {
  const modal = document.getElementById("searchModal");
  const input = document.getElementById("searchInput");

  if (modal) {
    modal.classList.remove("hidden");
  }

  if (input) {
    input.focus();
  }
}

function closeSearch() {
  const modal = document.getElementById("searchModal");

  if (modal) {
    modal.classList.add("hidden");
  }
}


// --------------------------------------------------
// Copy Publication Link
// --------------------------------------------------

document.addEventListener("DOMContentLoaded", function () {

  const copyButton = document.getElementById("copyLinkBtn");

  if (!copyButton) return;

  copyButton.addEventListener("click", async function () {

    try {

      await navigator.clipboard.writeText(window.location.href);

      const original = copyButton.innerHTML;

      copyButton.innerHTML = "✅ Copied!";

      setTimeout(function () {
        copyButton.innerHTML = original;
      }, 2000);

    } catch (err) {

      // Fallback for older browsers
      const textArea = document.createElement("textarea");
      textArea.value = window.location.href;

      document.body.appendChild(textArea);

      textArea.select();

      document.execCommand("copy");

      document.body.removeChild(textArea);

      const original = copyButton.innerHTML;

      copyButton.innerHTML = "✅ Copied!";

      setTimeout(function () {
        copyButton.innerHTML = original;
      }, 2000);
    }

  });

});

function copyPublicationLink() {

    navigator.clipboard.writeText(window.location.href);

    alert("Publication link copied successfully.");

}


// --------------------------------------------------
// Homepage Popup
// --------------------------------------------------

document.addEventListener("DOMContentLoaded", function () {
  const popup = document.getElementById("homepagePopup");

  if (!popup) {
    return;
  }

  const closeButtons = popup.querySelectorAll("[data-popup-close]");
  const focusableSelector = 'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])';
  let lastFocusedElement = null;

  function getFocusableElements() {
    return Array.from(popup.querySelectorAll(focusableSelector)).filter(function (element) {
      return element.offsetParent !== null;
    });
  }

  function openPopup() {
    lastFocusedElement = document.activeElement;
    popup.classList.remove("hidden");
    document.body.classList.add("popup-open");
    popup.focus();

    const focusable = getFocusableElements();
    if (focusable.length) {
      focusable[0].focus();
    }
  }

  function closePopup() {
    popup.classList.add("hidden");
    document.body.classList.remove("popup-open");

    if (lastFocusedElement && typeof lastFocusedElement.focus === "function") {
      lastFocusedElement.focus();
    }
  }

  closeButtons.forEach(function (button) {
    button.addEventListener("click", closePopup);
  });

  popup.addEventListener("click", function (event) {
    if (event.target === popup || event.target.classList.contains("site-popup__overlay")) {
      closePopup();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !popup.classList.contains("hidden")) {
      closePopup();
    }
  });

  setTimeout(openPopup, 100);
});
