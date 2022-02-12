const PATTERNS = new Map([
  ["archive", "https://web.archive.org/web/*/$path"],
  ["go", "http://localhost:8000/go/$path"],
  ["kg", "http://localhost:8000/$path"],
  ["s", "http://localhost:8000/search/$path"],
  ["todo", "http://localhost:8000/tasks/$path"],
  [
    "w",
    "https://www.wikipedia.org/search-redirect.php?family=wikipedia&language=en,en&search=$path&go=Go",
  ],
]);

/**
 * Redirects the request if appropriate.
 *
 * Note that if this function doesn't return anything, then Firefox will handle
 * the request normally.
 *
 * https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/webRequest
 */
function redirect(request) {
  const regex = /^http:\/\/([a-z]+)\/(.*)+$/;
  const match = regex.exec(request.url);
  if (!match) {
    return;
  }

  const domain = match[1];
  const path = match[2];

  const pattern = PATTERNS.get(domain);
  if (pattern) {
    return { redirectUrl: pattern.replace("$path", path) };
  } else {
    return;
  }
}

const urls = [];
for (const key of PATTERNS.keys()) {
  urls.push("http://" + key + "/*");
}

// `chrome` works in both Firefox and Chrome, while `browser` only works in
// Firefox: https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Build_a_cross_browser_extension
// eslint-disable-next-line no-undef
chrome.webRequest.onBeforeRequest.addListener(redirect, { urls }, ["blocking"]);
