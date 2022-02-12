<template>
  <loading-box class="page" :url="apiUrl" @data-loaded="entries = $event">
    <h1 class="text-center">Journal for {{ monthName }} {{ year }}</h1>

    <month-nav :year="year" :month="month" url="journal-month" />

    <b-row>
      <b-col>
        <h2 class="text-center">Journal entries</h2>
        <ul>
          <li v-for="entry in entries" :key="entry.date">
            <date-link :date="entry.date" />
          </li>
        </ul>
      </b-col>

      <b-col>
        <h2 class="text-center">Other information</h2>
        <ul>
          <li>
            <router-link
              :to="{ name: 'metrics-month', params: { year, month } }"
            >
              Metrics
            </router-link>
          </li>
          <li>
            <router-link
              :to="{ name: 'finances-month', params: { year, month } }"
            >
              Finances
            </router-link>
          </li>
          <li>
            <router-link
              :to="{ name: 'reading-month', params: { year, month } }"
            >
              Reading log
            </router-link>
          </li>
        </ul>
      </b-col>
    </b-row>
  </loading-box>
</template>

<script>
import { DateTime } from "luxon";

import { getMonthName } from "common.js";

export default {
  props: {
    year: { type: Number, required: true },
    month: { type: Number, required: true },
  },

  data() {
    return { entries: [] };
  },

  computed: {
    apiUrl() {
      return `/api/journal/entries/${this.year}/${this.month}`;
    },

    monthName() {
      return getMonthName(this.month);
    },

    earliest() {
      return DateTime.fromObject({ year: 2022, month: 2 });
    },
  },
};
</script>
