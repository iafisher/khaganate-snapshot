<template>
  <span v-if="isValidInput">
    <router-link
      :to="{
        name: 'journal-day',
        params: {
          year: dateAsObject.year,
          month: dateAsObject.month,
          day: dateAsObject.day,
        },
      }"
    >
      <slot>{{ dateAsString }}</slot></router-link
    ><template v-if="withTime">, {{ timeAsString }} </template>
  </span>
</template>

<script>
import { DateTime } from "luxon";

import { isNumber, isString } from "lodash";

export default {
  props: {
    date: { type: [Number, Object, String], required: false, default: null },
    withTime: { type: Boolean, default: false },
  },

  computed: {
    dateAsObject() {
      if (!this.isValidInput) {
        return null;
      }

      if (isString(this.date)) {
        // Check if it's just a date (without a time) and don't do the time-
        // zone conversion if so.
        if (/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(this.date)) {
          return DateTime.fromISO(this.date);
        } else {
          // Read the timestamp as UTC and then convert it to system time for
          // display.
          return DateTime.fromISO(this.date, { zone: "UTC" }).setZone();
        }
      } else if (isNumber(this.date)) {
        return DateTime.fromSeconds(this.date);
      } else {
        return this.date;
      }
    },

    dateAsString() {
      return this.dateAsObject.toLocaleString(DateTime.DATE_FULL);
    },

    isValidInput() {
      return this.date !== null && this.date !== "";
    },

    timeAsString() {
      return this.dateAsObject.toFormat("h:mm a ZZZZ");
    },
  },
};
</script>
