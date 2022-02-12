export function popup(message, { autoDismiss = false, danger = false }) {
  // Styles for these pop-ups are defined in common/static/khaganate.css

  let div = document.getElementById("popups");
  if (!div) {
    div = document.createElement("div");
    div.id = "popups";
    document.body.append(div);
  }

  const box = document.createElement("div");
  box.classList.add("popup-message");
  if (danger) {
    box.classList.add("popup-danger");
  }

  const p = document.createElement("p");
  p.textContent = message;

  let dismissButton = null;
  if (autoDismiss) {
    setTimeout(() => {
      // Courtesy of https://stackoverflow.com/questions/29017379
      box.style.opacity = "0";
      box.addEventListener("transitionend", () => {
        box.remove();
      });
    }, 3000);
  } else {
    // If the pop-up won't dismiss automatically, create a button to
    // dismiss it.
    dismissButton = document.createElement("button");
    dismissButton.classList.add("kg-btn");
    dismissButton.classList.add("kg-btn-secondary");
    dismissButton.textContent = "Dismiss";
    dismissButton.addEventListener("click", () => {
      box.remove();
    });
  }

  box.append(p);
  if (dismissButton !== null) {
    box.append(dismissButton);
  }
  // The boxes stack vertically, so prepending ensures that new messages
  // don't change the viewport position of existing ones.
  div.prepend(box);
}
