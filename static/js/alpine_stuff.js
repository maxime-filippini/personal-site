document.addEventListener("alpine:init", () => {
  Alpine.store("darkMode", {
    on:
      localStorage.getItem("darkMode") === "true" ||
      (!localStorage.getItem("darkMode") &&
        window.matchMedia("(prefers-color-scheme: black)").matches),

    init() {
      const html = document.documentElement;
      html.setAttribute("data-theme", this.on ? "black" : "lofi");
    },

    toggle() {
      this.on = !this.on;
      localStorage.setItem("darkMode", this.on);

      const html = document.documentElement;
      html.setAttribute("data-theme", this.on ? "black" : "lofi");
    },
  });

  // Initialize theme immediately
  Alpine.store("darkMode").init();
});
