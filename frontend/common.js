import * as lodash from "lodash";
import { DateTime } from "luxon";

/**
 * Returns the floating-point quantity formatted as a dollar amount.
 *
 *     formatDollarAmount(1.2)  === "$1.20"
 *     formatDollarAmount(-1.2) === "-$1.20"
 */
export function formatDollarAmount(x) {
  if (x >= 0) {
    return "$" + formatIntegerWithCommas(x.toFixed(2));
  } else {
    return "-$" + formatIntegerWithCommas((-x).toFixed(2));
  }
}

/**
 * Returns the integer as a string with a comma inserted between every third
 * digit.
 *
 *     formatIntegerWithCommas(1200000) === "1,200,000"
 */
export function formatIntegerWithCommas(x) {
  let xAsStr = "" + x;
  const regex = /(\d+)(\d{3})/;
  while (regex.test(xAsStr)) {
    xAsStr = xAsStr.replace(regex, "$1,$2");
  }
  return xAsStr;
}

export const MONTHS = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];
const MONTHS_INDEXED = [""].concat(MONTHS);

/**
 * Returns the name of the month with the given index, where 1 is January and
 * 12 is December.
 */
export function getMonthName(monthIndex) {
  if (monthIndex < 1 || monthIndex > 12) {
    throw "monthIndex out of bounds";
  }

  return MONTHS_INDEXED[monthIndex];
}

/**
 * Returns the correct plural or singular form of `singular` based on the
 * quantity `n`. If `plural` is provided, it is used as the plural form.
 * Otherwise, the plural is formed by concatenating `"s"` to the end of
 * `singular`.
 */
export function pluralize(n, singular, plural) {
  if (n === 1) {
    return n + " " + singular;
  } else {
    return n + " " + (plural ? plural : singular + "s");
  }
}

export const MARKDOWN_OPTIONS = {
  html: true,
  linkify: true,
  // This causes (c) to become the copyright symbol, which is undesirable. See
  // GitHub issue #514.
  // typographer: true,
};

/**
 * Preprocesses Markdown text to turn short links into regular Markdown links.
 */
export function preprocessMarkdown(text) {
  return text.replace(
    /\b(files|go|kg|todo)\/([A-Za-z0-9/.-]*[A-Za-z0-9/-])\b/g,
    "[$1/$2](http://$1/$2)"
  );
}

/**
 * Formats the number of minutes since midnight as a human-readable time
 * string.
 *
 *     formatTime(120) === "2:00 am"
 */
export function formatTime(minutes) {
  const hours = Math.floor(minutes / 60);
  const leftoverMinutes = (minutes - hours * 60 + "").padStart(2, "0");

  // The hex code A0 is for the non-breaking space.
  if (hours === 0) {
    return `12:${leftoverMinutes}\xa0am`;
  } else if (hours < 13) {
    return `${hours}:${leftoverMinutes}\xa0am`;
  } else if (hours === 12) {
    return `12:${leftoverMinutes}\xa0pm`;
  } else {
    return `${hours - 12}:${leftoverMinutes}\xa0pm`;
  }
}

/**
 * Formats the ISO 8601 date string in a human-readable fashion.
 *
 *     formatDate("2021-08-23") === "August 23, 2021"
 */
export function formatDate(date) {
  return DateTime.fromISO(date).toFormat("LLLL d, y");
}

/**
 * Converts a time string to the number of minutes since midnight.
 *
 *     convertTimeStringToMinutes("2:00") === 120
 *
 * This function does not work on the output of `formatTime` since it can't
 * handle 'am' and 'pm' suffixes.
 */
export function convertTimeStringToMinutes(timeString) {
  const splitTimeString = timeString.split(":");
  return parseInt(splitTimeString[0]) * 60 + parseInt(splitTimeString[1]);
}

/**
 * Returns a Promise that immediately resolves to `x`.
 */
export function immediatePromise(x) {
  return new Promise(function (resolve) {
    resolve(x);
  });
}

/**
 * Recursively converts all keys of the object or array to camel-case.
 */
export function toCamelCase(o) {
  if (lodash.isArray(o)) {
    return o.map((x) => toCamelCase(x));
  } else if (lodash.isObject(o)) {
    return lodash.transform(o, (r, v, k) => {
      r[lodash.camelCase(k)] = toCamelCase(v);
    });
  } else {
    return o;
  }
}

export function formatMetricValue(type, value) {
  if (value === null) {
    return "";
  }

  if (type === "dollar") {
    return formatDollarAmount(value);
  } else if (type === "time") {
    if (lodash.isString(value)) {
      value = convertTimeStringToMinutes(value);
    }

    return formatTime(value);
  } else if (type === "duration") {
    const hours = Math.floor(value / 60);
    const minutes = Math.floor(value % 60);

    if (minutes === 0) {
      return `${hours}h`;
    } else {
      return `${hours}h ${minutes}m`;
    }
  } else if (type === "percentage") {
    return (value * 100).toFixed(1) + "%";
  } else if (type === "integer") {
    return formatIntegerWithCommas(Math.round(value));
  } else {
    return value;
  }
}
