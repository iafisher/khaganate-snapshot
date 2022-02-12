import * as axios from "axios";

import * as popupService from "services/popup_service.js";
import { toCamelCase } from "common.js";

const CSRF = getCsrfToken();

export function get(url) {
  return axios
    .get(url)
    .then((response) => {
      const contentType = response.headers["content-type"];
      if (contentType !== "application/json") {
        const message = `API returned non-JSON response (${contentType})`;
        genericApiError("GET", url, message);
        throw message;
      }

      console.group(`apiService.get (${url})`);
      console.debug(response);
      console.debug(response.data);
      console.groupEnd();

      return toCamelCase(response.data);
    })
    .catch((error) => {
      apiError("GET", url, error);
      throw error;
    });
}

export function post(url, payload) {
  return axios
    .post(url, payload, { headers: { "X-CSRFToken": CSRF } })
    .then((response) => {
      const contentType = response.headers["content-type"];
      if (contentType !== "application/json") {
        const message = `API returned non-JSON response (${contentType})`;
        genericApiError("POST", url, message);
        throw message;
      }

      console.group(`apiService.post (${url})`);
      console.debug("POST payload:", payload);
      console.debug(response);
      console.debug(response.data);
      console.groupEnd();

      return toCamelCase(response.data);
    })
    .catch((error) => {
      apiError("POST", url, error);
      console.error("POST payload:", payload);
      throw error;
    });
}

function apiError(verb, url, error) {
  // https://axios-http.com/docs/handling_errors
  let message;
  if (error.response) {
    message = `server error ${error.response.status}.`;
  } else if (error.request) {
    message = "could not connect to server.";
  } else {
    message = "could not initialize request.";
  }
  console.error(message);
  genericApiError(verb, url, message);
}

function genericApiError(verb, url, message) {
  message = `${verb} request to '${url}' failed: ${message}`;
  console.error(message);
  popupService.popup(message, { danger: true });
}

function getCsrfToken() {
  const e = document.querySelector('input[name="csrfmiddlewaretoken"]');
  return e.value;
}
