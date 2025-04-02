// fix for jerking animation when page loads
window.addEventListener("load", function () {
  document.querySelector("body").classList.remove("preload");
});
