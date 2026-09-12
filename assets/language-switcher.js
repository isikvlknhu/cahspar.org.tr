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
    var collapse = document.getElementById("navbarCollapse");
    if (!collapse) return;

    document.addEventListener("click", function (event) {
      var toggler = event.target.closest(".navbar-toggler[data-bs-target='#navbarCollapse']");
      if (!toggler) return;

      event.preventDefault();
      event.stopImmediatePropagation();

      var isOpen = collapse.classList.toggle("show");
      collapse.classList.remove("collapsing");
      collapse.classList.add("collapse");
      toggler.setAttribute("aria-expanded", String(isOpen));
    }, true);
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
