<template>
  <loading-box
    class="container"
    :url="apiUrl"
    :refresh-silently="refresh + refreshInternal"
    @data-loaded="onDataLoaded"
  >
    <h2>Goals for {{ monthName }}</h2>
    <b-progress height="0.5rem" variant="secondary">
      <b-progress-bar :value="daysElapsedInMonth" :max="31"></b-progress-bar>
    </b-progress>
    <template v-if="goalsForMonth.length > 0">
      <goal-entry
        v-for="goal in goalsForMonth"
        :key="goal.id"
        class="goal"
        :goal="goal"
        @goal-progress-updated="onProgressUpdated($event)"
      />
    </template>
    <template v-else>
      <p>No goals set.</p>
    </template>

    <h2>Goals for Q{{ quarter }}</h2>
    <b-progress height="0.5rem" variant="secondary">
      <b-progress-bar
        :value="daysElapsedInQuarter"
        :max="31 * 3"
      ></b-progress-bar>
    </b-progress>
    <template v-if="goalsForQuarter.length > 0">
      <goal-entry
        v-for="goal in goalsForQuarter"
        :key="goal.id"
        class="goal"
        :goal="goal"
        @goal-progress-updated="onProgressUpdated($event)"
      />
    </template>
    <template v-else>
      <p>No goals set.</p>
    </template>

    <h2>Goals for {{ year }}</h2>
    <b-progress height="0.5rem" variant="secondary">
      <b-progress-bar :value="daysElapsedInYear" :max="365"></b-progress-bar>
    </b-progress>
    <template v-if="goalsForYear.length > 0">
      <goal-entry
        v-for="goal in goalsForYear"
        :key="goal.id"
        class="goal"
        :goal="goal"
        @goal-progress-updated="onProgressUpdated($event)"
      />
    </template>
    <template v-else>
      <p>No goals set.</p>
    </template>
  </loading-box>
</template>

<script>
import { DateTime } from "luxon";

import GoalEntry from "./GoalEntry.vue";

export default {
  components: {
    GoalEntry,
  },
  props: {
    year: { type: Number, required: true },
    month: { type: Number, required: true },
    refresh: { type: Number, required: false, default: 0 },
  },

  data() {
    return {
      goalsForMonth: [],
      goalsForQuarter: [],
      goalsForYear: [],
      refreshInternal: 0,
    };
  },

  computed: {
    apiUrl() {
      const month = ("" + this.month).padStart(2, "0");
      return `/api/goals/list/${this.year}/${month}`;
    },

    daysElapsedInMonth() {
      return Math.floor(
        this.todayAdjusted().diff(this.startOfMonth, "days").days
      );
    },

    daysElapsedInQuarter() {
      return Math.floor(
        this.todayAdjusted().diff(this.startOfQuarter, "days").days
      );
    },

    daysElapsedInYear() {
      return Math.floor(
        this.todayAdjusted().diff(DateTime.local(this.year, 1, 1), "days").days
      );
    },

    monthName() {
      return this.startOfMonth.toFormat("LLLL");
    },

    quarter() {
      const month = this.todayAdjusted().month;
      return Math.floor((month - 1) / 3) + 1;
    },

    startOfMonth() {
      return DateTime.local(this.year, this.todayAdjusted().month, 1);
    },

    startOfQuarter() {
      const startOfQuarterMonth = (this.quarter - 1) * 3 + 1;
      return DateTime.local(this.year, startOfQuarterMonth, 1);
    },
  },

  methods: {
    onDataLoaded(data) {
      this.goalsForMonth = data.monthGoals;
      this.goalsForQuarter = data.quarterGoals;
      this.goalsForYear = data.yearGoals;
    },

    onProgressUpdated(event) {
      this.$apiPost(`/api/db/update/goals/${event.goal.id}`, {
        progress: event.goal.progress + event.amount,
      }).then(() => {
        this.refreshInternal++;
      });
    },
  },
};
</script>

<style scoped>
.container {
  min-width: 400px;
}

.goal {
  margin-top: 10px;
}

.goal + h2 {
  margin-top: 30px;
}
</style>
