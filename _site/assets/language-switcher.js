(function () {
  function getTargetLanguage(link) {
    var label = (link.textContent || "").trim().toUpperCase();
    if (label === "EN") return "en";
    if (label === "FR") return "fr";
    if (label === "ES") return "es";
    return null;
  }

  function buildTranslateUrl(targetLang) {
    var currentUrl = window.location.href;
    return "https://translate.google.com/translate?sl=tr&tl=" + targetLang + "&u=" + encodeURIComponent(currentUrl);
  }

  function bindLanguageSwitcher() {
    var links = document.querySelectorAll(".navbar-nav.ms-auto .nav-link");
    if (!links.length) return;

    links.forEach(function (link) {
      var targetLang = getTargetLanguage(link);
      if (!targetLang) return;

      link.setAttribute("href", buildTranslateUrl(targetLang));
      link.addEventListener("click", function (event) {
        event.preventDefault();
        window.location.href = buildTranslateUrl(targetLang);
      });
    });
  }

  function bindMobileNavigation() {
    var toggler = document.querySelector(".navbar-toggler[data-bs-target='#navbarCollapse']");
    var collapse = document.getElementById("navbarCollapse");
    if (!toggler || !collapse) return;

    toggler.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopImmediatePropagation();

      var isOpen = collapse.classList.toggle("show");
      collapse.classList.remove("collapsing");
      collapse.classList.add("collapse");
      toggler.setAttribute("aria-expanded", String(isOpen));
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      bindLanguageSwitcher();
      bindMobileNavigation();
    });
  } else {
    bindLanguageSwitcher();
    bindMobileNavigation();
  }
})();
