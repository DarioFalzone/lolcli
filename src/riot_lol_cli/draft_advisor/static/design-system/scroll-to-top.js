/**
 * Pattern transversal: botón flotante "Volver arriba".
 *
 * Auto-inicializa al cargar. Aparece cuando scrollY > 320, click hace scroll
 * suave al top. Compatible con cualquier frontend del repo que importe este
 * script desde /design-system/scroll-to-top.js.
 *
 * Uso:
 *   <script src="/design-system/scroll-to-top.js"></script>
 *
 * Si querés reinicializarlo manualmente (ej. tras navegación SPA con hash router),
 * llamá a window.LOLCLI_ScrollToTop.refresh()
 */
(function () {
  "use strict";

  const SCROLL_THRESHOLD = 320;
  const BUTTON_ID = "lolcli-scroll-to-top";

  function build() {
    if (document.getElementById(BUTTON_ID)) return document.getElementById(BUTTON_ID);
    const btn = document.createElement("button");
    btn.id = BUTTON_ID;
    btn.type = "button";
    btn.className = "scroll-to-top";
    btn.setAttribute("aria-label", "Volver arriba");
    btn.setAttribute("title", "Volver arriba");
    btn.innerHTML =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" ' +
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '<polyline points="6 14 12 8 18 14"/></svg>';
    btn.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
    document.body.appendChild(btn);
    return btn;
  }

  function updateVisibility(btn) {
    if (window.scrollY > SCROLL_THRESHOLD) {
      btn.classList.add("scroll-to-top--visible");
    } else {
      btn.classList.remove("scroll-to-top--visible");
    }
  }

  function init() {
    const btn = build();
    const onScroll = function () {
      updateVisibility(btn);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    updateVisibility(btn);

    // API mínima para SPAs con hash router (los apps que re-pintan el DOM al
    // cambiar de vista pueden llamar refresh() para asegurarse de que el botón
    // sigue existiendo en el body).
    window.LOLCLI_ScrollToTop = {
      refresh: function () {
        build();
        updateVisibility(document.getElementById(BUTTON_ID));
      },
    };
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
