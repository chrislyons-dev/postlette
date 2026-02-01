(() => {
  const setFavicon = (path) => {
    let link = document.querySelector('link[rel="icon"]');
    if (!link) {
      link = document.createElement("link");
      link.rel = "icon";
      document.head.appendChild(link);
    }
    link.href = path;
  };

  const update = () => {
    const scheme = document.documentElement.getAttribute("data-md-color-scheme");
    if (scheme === "slate") {
      setFavicon("images/logo-light.svg");
    } else {
      setFavicon("images/logo-dark.svg");
    }
  };

  const observer = new MutationObserver(update);
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-md-color-scheme"],
  });

  update();
})();
