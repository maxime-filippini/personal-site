(function () {
  const darkMode =
    localStorage.getItem("darkMode") === "true" ||
    (!localStorage.getItem("darkMode") &&
      window.matchMedia("(prefers-color-scheme: dark)").matches);
  document.documentElement.setAttribute(
    "data-theme",
    darkMode ? "black" : "lofi"
  );
})();
