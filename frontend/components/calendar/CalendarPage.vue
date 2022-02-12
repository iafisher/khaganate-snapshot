<template>
  <div class="page-very-wide">
    <h1 class="text-center">Week of {{ startOfWeekAsString }}</h1>
    <p class="text-center">
      <router-link
        class="mr-3"
        :to="{
          name: 'calendar',
          params: {
            year: weekBefore.year,
            month: weekBefore.month,
            day: weekBefore.day,
          },
        }"
      >
        &lt; previous week
      </router-link>
      <router-link
        class="ml-3 mr-3"
        :to="{
          name: 'calendar',
          params: {
            year: todayAdjusted().year,
            month: todayAdjusted().month,
            day: todayAdjusted().day,
          },
        }"
      >
        today
      </router-link>
      <router-link
        class="ml-3"
        :to="{
          name: 'calendar',
          params: {
            year: weekAfter.year,
            month: weekAfter.month,
            day: weekAfter.day,
          },
        }"
      >
        next week &gt;
      </router-link>
    </p>

    <div class="calendar-box">
      <calendar-range :start="start" :end="end" :refresh="refresh" />
    </div>
  </div>
</template>

<script>
import { DateTime } from "luxon";

import CalendarRange from "./CalendarRange.vue";

export default {
  components: {
    CalendarRange,
  },
  props: {
    year: { type: Number, required: true },
    month: { type: Number, required: true },
    day: { type: Number, required: true },
  },

  data() {
    return { refresh: 0 };
  },

  computed: {
    start() {
      return this.date.startOf("week");
    },

    end() {
      return this.start.plus({ days: 6 });
    },

    date() {
      return DateTime.fromObject({
        year: this.year,
        month: this.month,
        day: this.day,
      });
    },

    startOfWeek() {
      return this.date.startOf("week");
    },

    startOfWeekAsString() {
      return this.startOfWeek.toLocaleString(DateTime.DATE_FULL);
    },

    weekBefore() {
      return this.startOfWeek.minus({ days: 7 });
    },

    weekAfter() {
      return this.startOfWeek.plus({ days: 7 });
    },
  },

  watch: {
    $route() {
      this.refresh++;
    },
  },
};
</script>

<style scoped>
.calendar-box {
  display: flex;
  flex-direction: row;
  justify-content: center;
}
</style>
