<template>
  <div class="page-wide">
    <h1 class="text-center">journal</h1>

    <p>
      <date-link :date="today">today</date-link>
    </p>

    <div v-for="year in years" :key="year">
      <h3>{{ year }}</h3>

      <p>
        <router-link
          v-for="month in getMonths(year)"
          :key="month"
          class="spaced-inline"
          :to="{ name: 'journal-month', params: { year, month } }"
        >
          {{ getMonthName(month).toLowerCase() }}
        </router-link>
      </p>
    </div>
  </div>
</template>

<script>
import * as lodash from "lodash";
import { DateTime } from "luxon";

import { getMonthName } from "common.js";

const FIRST_YEAR_OF_JOURNAL = 2022;

export default {
  computed: {
    today() {
      return DateTime.local();
    },

    years() {
      const years = [];
      let year = this.today.year;
      while (year >= FIRST_YEAR_OF_JOURNAL) {
        years.push(year);
        year--;
      }
      return years;
    },
  },

  methods: {
    getMonths(year) {
      const now = DateTime.local();
      if (year === now.year) {
        return lodash.range(1, now.month + 1);
      } else {
        return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
      }
    },

    getMonthName: getMonthName,
  },
};
</script>
