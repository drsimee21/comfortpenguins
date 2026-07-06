(function () {
  var productImage = document.querySelector(".product-image");

  if (productImage) {
    productImage.addEventListener("error", function () {
      var fallback = productImage.getAttribute("data-fallback");
      if (fallback && productImage.getAttribute("src") !== fallback) {
        productImage.setAttribute("src", fallback);
      }
    });
  }

  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener("click", function (event) {
      var targetId = link.getAttribute("href");
      var target = targetId ? document.querySelector(targetId) : null;
      if (!target) {
        return;
      }

      event.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  var thankYouScreen;
  var lastFocusedElement;

  function createThankYouScreen() {
    var screen = document.createElement("section");
    screen.className = "thank-you-screen";
    screen.hidden = true;
    screen.setAttribute("role", "dialog");
    screen.setAttribute("aria-modal", "true");
    screen.setAttribute("aria-labelledby", "thank-you-title");
    screen.setAttribute("aria-describedby", "thank-you-message");

    var panel = document.createElement("div");
    panel.className = "thank-you-panel";

    var animation = document.createElement("div");
    animation.className = "thank-you-animation";
    animation.setAttribute("aria-hidden", "true");

    var parade = document.createElement("div");
    parade.className = "thank-you-parade";
    parade.setAttribute("aria-hidden", "true");

    var content = document.createElement("div");
    content.className = "thank-you-content";

    var mark = document.createElement("span");
    mark.className = "heart-mark heart-mark--cream thank-you-mark";
    mark.setAttribute("aria-hidden", "true");
    mark.textContent = "\u2661";

    var title = document.createElement("h2");
    title.id = "thank-you-title";
    title.textContent = "Thank you for joining the Comfort Penguin family. \u2661";

    var message = document.createElement("p");
    message.id = "thank-you-message";
    message.textContent = "We'll be in touch when Comfort Penguins is ready to launch.";

    var closeButton = document.createElement("button");
    closeButton.className = "button button--primary thank-you-close";
    closeButton.type = "button";
    closeButton.textContent = "Back to the page";
    closeButton.addEventListener("click", hideThankYouScreen);

    content.append(mark, title, message, closeButton);
    panel.appendChild(content);
    screen.append(animation, parade, panel);
    document.body.appendChild(screen);

    screen.addEventListener("click", function (event) {
      if (event.target === screen) {
        hideThankYouScreen();
      }
    });

    return screen;
  }

  function showThankYouScreen() {
    if (!thankYouScreen) {
      thankYouScreen = createThankYouScreen();
    }

    lastFocusedElement = document.activeElement;
    thankYouScreen.hidden = false;
    document.body.classList.add("thank-you-open");

    var content = thankYouScreen.querySelector(".thank-you-content");
    if (content) {
      content.classList.remove("thank-you-content--visible");
      window.setTimeout(function () {
        content.classList.add("thank-you-content--visible");
      }, 120);
    }

    var animation = thankYouScreen.querySelector(".thank-you-animation");
    if (animation && window.ComfortPenguinConfetti) {
      window.ComfortPenguinConfetti.build(animation);
    }

    var parade = thankYouScreen.querySelector(".thank-you-parade");
    if (parade && window.ComfortPenguinParade) {
      window.ComfortPenguinParade.build(parade);
    }

    var closeButton = thankYouScreen.querySelector(".thank-you-close");
    if (closeButton) {
      closeButton.focus({ preventScroll: true });
    }
  }

  function hideThankYouScreen() {
    if (!thankYouScreen || thankYouScreen.hidden) {
      return;
    }

    thankYouScreen.hidden = true;
    document.body.classList.remove("thank-you-open");

    if (lastFocusedElement && lastFocusedElement.focus) {
      lastFocusedElement.focus({ preventScroll: true });
    }
  }

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      hideThankYouScreen();
    }
  });

  document.addEventListener("formspace:submit", function () {
    window.setTimeout(showThankYouScreen, 250);
  });

  window.ComfortPenguinSuccess = {
    show: showThankYouScreen,
    hide: hideThankYouScreen,
  };

  if (document.body && document.body.dataset.celebrateOnLoad === "true") {
    window.setTimeout(showThankYouScreen, 500);
  }
})();
