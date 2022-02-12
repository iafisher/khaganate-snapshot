// Make sure these matches the values in the stylesheet of `CalendarDay.vue`.
export const CALENDAR_HEIGHT = 600;
export const EVENT_HEIGHT = 42;

const START_TIME = 8 * 60; // 8am
const END_TIME = 24 * 60; // midnight

export function durationToHeight(minutes) {
  const r = (END_TIME - START_TIME) / CALENDAR_HEIGHT;
  return Math.floor(minutes / r);
}

export function timeToPosition(minutes) {
  if (minutes <= START_TIME) {
    return 0;
  } else if (minutes >= END_TIME) {
    return CALENDAR_HEIGHT - EVENT_HEIGHT;
  } else {
    return durationToHeight(minutes - START_TIME);
  }
}

export function getMapsUrl(event) {
  let location = event.location;

  // If the location ends with a parenthesized aside, remove it before
  // passing it to Google Maps.
  if (location.endsWith(")")) {
    const start = location.lastIndexOf("(");
    if (start !== -1) {
      location = location.slice(0, start).trim();
    }
  }

  return "https://google.com/maps/place/" + location;
}
