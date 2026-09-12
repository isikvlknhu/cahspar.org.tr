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
    var toggler = document.querySelector(".navbar-toggler[data-bs-target='#navbarCollapse']");
    if (!collapse || !toggler) return;

    var bsCollapse = null;
    if (window.bootstrap && window.bootstrap.Collapse) {
      bsCollapse = window.bootstrap.Collapse.getOrCreateInstance(collapse, { toggle: false });
    }

    function setMenuState(isOpen) {
      if (bsCollapse) {
        if (isOpen) {
          bsCollapse.show();
        } else {
          bsCollapse.hide();
        }
        return;
      }

      collapse.classList.toggle("show", isOpen);
      collapse.classList.remove("collapsing");
      collapse.classList.add("collapse");
      toggler.setAttribute("aria-expanded", String(isOpen));
    }

    document.addEventListener("click", function (event) {
      var target = event.target;
      var clickedToggler = target.closest(".navbar-toggler[data-bs-target='#navbarCollapse']");
      var clickedItem = target.closest(".nav-link, .dropdown-item");

      if (clickedToggler && window.innerWidth < 992) {
        event.preventDefault();
        event.stopPropagation();
        setMenuState(!collapse.classList.contains("show"));
        return;
      }

      if (clickedItem && window.innerWidth < 992) {
        var href = clickedItem.getAttribute("href");
        setMenuState(false);
        if (href && href !== "#") {
          window.location.href = href;
        }
      }
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
