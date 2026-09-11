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

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindLanguageSwitcher);
  } else {
    bindLanguageSwitcher();
  }
})();
