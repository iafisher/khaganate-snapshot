/**
 * This is a content script which popup.js executes and which, unlike popup.js,
 * runs on the actual page instead of the popup window. It is used to extract
 * values of <meta> elements.
 */

// Wrapping the script in an anonymous function prevents name collisions with
// variables declared by other scripts.
(function () {
  const meta = {};

  for (const e of document.getElementsByTagName("meta")) {
    if (e.hasAttribute("name")) {
      meta[e.getAttribute("name")] = e.getAttribute("content");
    } else if (e.getAttribute("itemprop")) {
      meta[e.getAttribute("itemprop")] = e.getAttribute("content");
    } else if (e.getAttribute("property")) {
      meta[e.getAttribute("property")] = e.getAttribute("content");
    }
  }

  // A content script returns the value of the last line of code executed to
  // its caller. So if this code wasn't wrapped in an anonymous function, the
  // last line of the script would simply be
  //
  //   meta;
  //
  // in order to return the value of `meta` to the caller.
  return meta;
})();
