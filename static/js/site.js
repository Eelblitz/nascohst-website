function toggleMenu() {
  var menu = document.getElementById('mobileMenu');
  if (!menu) {
    return;
  }
  menu.classList.toggle('hidden');
}

function openSearch() {
  var modal = document.getElementById('searchModal');
  var input = document.getElementById('searchInput');
  if (modal) {
    modal.classList.remove('hidden');
  }
  if (input) {
    input.focus();
  }
}

function closeSearch() {
  var modal = document.getElementById('searchModal');
  if (modal) {
    modal.classList.add('hidden');
  }
}
