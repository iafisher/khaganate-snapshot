/* Declare `browser` and `$` as globals to satisfy ESLint. */
/* global browser */
/* global $ */
"use strict";

const SELECT_TOPICS = 'select[name="topics"]';

async function onLoad(savedFolderId) {
  // Initialize the input boxes for topics.
  initializeSelect2();

  const tabs = await browser.tabs.query({ currentWindow: true, active: true });
  const tab = tabs[0];
  const url = tab.url;

  // Use a content script to load the <meta> values from the page, since the
  // pop-up window can't access the page directly.
  const contentScriptResults = await browser.tabs.executeScript({
    file: "/content-script.js",
  });
  const meta = contentScriptResults[0];

  // Check if the bookmark already exists in the browser.
  const searchResults = await browser.bookmarks.search({ url });

  // Check if the bookmark already exists in Khaganate and fill in its details
  // if it does.
  showLoader();
  let response;
  try {
    response = await fetch(
      "http://localhost:8000/api/tags/bookmark/get?url=" +
        encodeURIComponent(url)
    );
  } catch (err) {
    console.error(err);
    showError("could not fetch bookmark from Khaganate: " + err);
    return;
  } finally {
    hideLoader();
  }

  const payload = await response.json();
  const details = {
    bookmark: payload.bookmark,
    browserBookmark: searchResults.length > 0 ? searchResults[0] : null,
    url: url,
  };
  if (payload.bookmark) {
    id("update-form").style.display = "block";
    id("create-form").remove();

    getInput("title").value = payload.bookmark.title;
    getInput("url").value = tab.url;
    getInput("author").value = payload.bookmark.author;
    getInput("year").value = payload.bookmark.year;
    getInput("keywords").value = payload.bookmark.keywords;
    getSelect("quality").value = payload.bookmark.quality;
    getTextarea("annotation").value = payload.bookmark.annotation;

    const topicsList = document.getElementById("topics-list");
    for (const topic of payload.bookmark.topics) {
      addSelect2Option($(SELECT_TOPICS), topic.id, topic.path);
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.textContent = topic.path;
      a.setAttribute("href", "http://kg/biblio/" + topic.path);
      a.setAttribute("target", "_blank");
      li.append(a);
      topicsList.append(li);
    }

    id("button-update").addEventListener("click", () =>
      saveBookmark(savedFolderId, details)
    );
    id("button-delete").addEventListener("click", () =>
      deleteBookmark(savedFolderId, details)
    );
  } else {
    id("create-form").style.display = "block";
    id("update-form").remove();
    // Pre-fill title and URL fields from the current tab.
    getInput("title").value = tab.title;
    getInput("url").value = tab.url;
    getInput("author").value = guessAuthor(tab, meta);
    getInput("year").value = guessYear(tab, meta);

    id("button-create").addEventListener("click", () =>
      saveBookmark(savedFolderId, details)
    );
  }

  // Focus the input box for keywords.
  getInput("keywords").focus();
}

async function saveBookmark(savedFolderId, details) {
  const title = getInputValue("title");
  const url = getInputValue("url");
  const author = getInputValue("author");
  const year = getInputValue("year");
  const keywords = getInputValue("keywords");
  const quality = getSelect("quality").value;
  const annotation = getTextareaValue("annotation");

  let topics = [];
  for (const selection of $(SELECT_TOPICS).select2("data")) {
    topics.push({ id: selection.id, path: selection.text });
  }

  if (title === "") {
    showError("title is required");
    return;
  }

  if (url === "") {
    showError("url is required");
    return;
  }

  if (!getInput("url").checkValidity()) {
    showError("url is invalid");
    return;
  }

  hideError();
  showLoader();

  const options = {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      id: details.bookmark ? details.bookmark.id : null,
      title: title,
      url: url,
      keywords: keywords,
      topics: topics,
      author: author,
      year: year,
      quality: quality,
      annotation: annotation,
    }),
  };

  let response;
  try {
    response = await fetch(
      "http://localhost:8000/api/tags/bookmark/create",
      options
    );
  } catch (err) {
    console.error(err);
    showError("could not create bookmark in Khaganate: " + err);
    return;
  } finally {
    hideLoader();
  }

  const payload = await response.json();
  if (payload.error) {
    showError(payload.error);
    return;
  }

  if (!details.browserBookmark) {
    try {
      await browser.bookmarks.create({
        parentId: savedFolderId,
        title: title,
        url: url,
      });
    } catch (err) {
      console.error(err);
      showError("could not create bookmark in the browser: " + err);
      return;
    }
  } else if (details.browserBookmark.parentId !== savedFolderId) {
    try {
      await browser.bookmarks.move(details.browserBookmark.id, {
        parentId: savedFolderId,
      });
    } catch (err) {
      console.error(err);
      showError(
        "could not move bookmark to Saved folder in the browser: " + err
      );
      return;
    }
  }

  window.close();
}

async function deleteBookmark(savedFolderId, details) {
  showLoader();

  const options = {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      id: details.bookmark.id,
    }),
  };

  let response;
  try {
    response = await fetch(
      "http://localhost:8000/api/tags/bookmark/delete",
      options
    );
  } catch (err) {
    console.error(err);
    showError("could not delete bookmark in Khaganate: " + err);
    return;
  } finally {
    hideLoader();
  }

  const payload = await response.json();
  if (payload.error) {
    showError(payload.error);
    return;
  }

  if (
    details.browserBookmark &&
    details.browserBookmark.parentId === savedFolderId
  ) {
    try {
      await browser.bookmarks.remove(details.browserBookmark.id);
    } catch (err) {
      console.error(err);
      showError("could not delete bookmark in the browser: " + err);
      return;
    }
  }

  window.close();
}

function guessAuthor(tab, meta) {
  // Site-specific logic
  const url = new URL(tab.url);
  if (hasHostName(url, "nytimes.com")) {
    if (meta.byl && meta.byl.startsWith("By ")) {
      return meta.byl.slice(3);
    }
  }

  // Generic logic
  if (meta.author) {
    return meta.author;
  }

  return "";
}

function guessYear(tab, meta) {
  const possibilities = guessYearNaive(tab, meta);
  for (const possibility of possibilities) {
    if (!!possibility && dateHasYear(possibility)) {
      return possibility.slice(0, 4);
    }
  }

  return "";
}

function guessYearNaive(tab, meta) {
  const possibilities = [];

  // Site-specific logic
  const url = new URL(tab.url);
  if (hasHostName(url, "nytimes.com")) {
    return [meta.pdate];
  }

  // Generic logic
  possibilities.push(meta.datePublished);
  possibilities.push(meta["article:published_time"]); // medium.com
  return possibilities;
}

function initializeSelect2() {
  $(SELECT_TOPICS).select2(
    getSelect2Settings("http://localhost:8000/api/tags/topic/search")
  );
}

function getSelect2Settings(url) {
  return {
    ajax: {
      url,
      dataType: "json",
    },
    createTag: function (params) {
      // Attach a `newTag` property for `templateResult`.
      return {
        id: params.term,
        text: params.term,
        newTag: true,
      };
    },
    insertTag: function (data, tag) {
      // Place "Create '___'" options at the end of the list.
      data.push(tag);
    },
    minimumInputLength: 1,
    tags: true,
    templateResult: function (tag) {
      // Display text as "Create '___'" for new tags by checking the `newTag`
      // property that would have been attached in `createTag`.
      return tag.newTag ? `Create '${tag.text}'` : tag.text;
    },
    width: "100%",
  };
}

function addSelect2Option(el, id, text) {
  const option = new Option(text, id, true, true);
  el.append(option).trigger("change");
  el.trigger({
    type: "select2:select",
    params: {
      data: {
        id: id,
        text: text,
      },
    },
  });
}

function getInput(name) {
  return q('input[name="' + name + '"]');
}

function getInputValue(name) {
  return getInput(name).value.trim();
}

function getTextarea(name) {
  return q('textarea[name="' + name + '"]');
}

function getTextareaValue(name) {
  return getTextarea(name).value.trim();
}

function getSelect(name) {
  return q('select[name="' + name + '"]');
}

function showError(message) {
  id("error-message").textContent = message;
  id("error").style.display = "block";
}

function hideError() {
  id("error").style.display = "none";
}

function showLoader() {
  id("loader").style.display = "block";
}

function hideLoader() {
  id("loader").style.display = "none";
}

function id(x) {
  return document.getElementById(x);
}

function q(x) {
  return document.querySelector(x);
}

function hasHostName(url, hostName) {
  return url.hostname === hostName || url.hostname.endsWith("." + hostName);
}

function dateHasYear(date) {
  return date.match(/^[0-9]{4}/);
}

browser.bookmarks
  .search({ title: "Saved" })
  .then((results) => {
    if (results.length === 0) {
      showError("Could not find Saved bookmarks folder.");
    } else {
      onLoad(results[0].id);
    }
  })
  .catch((error) => {
    console.error(error);
    showError("Error while trying to fetch Saved bookmarks folder.");
  });
