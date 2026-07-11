// --------------------------------------------------
// Mobile Navigation
// --------------------------------------------------

function toggleMenu() {
  const menu = document.getElementById("mobileMenu");

  if (menu) {
    menu.classList.toggle("hidden");
  }
}


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