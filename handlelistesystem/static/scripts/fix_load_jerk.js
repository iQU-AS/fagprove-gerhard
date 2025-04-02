// fix for jerking animation when page loads
document.addEventListener("load", function () {
  document.querySelector("body").classList.remove("preload");
});
