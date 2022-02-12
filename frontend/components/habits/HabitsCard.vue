<template>
  <loading-box
    :url="apiUrls"
    :refresh-silently="refresh"
    @data-loaded="onDataLoaded"
  >
    <div class="badges">
      <b-badge
        v-for="habit in habitsSorted"
        :key="habit.id"
        class="cursor"
        pill
        :variant="habit.points > 0 ? 'success' : 'danger'"
        @click="onClick(habit)"
      >
        {{ habit.name }}
      </b-badge>
    </div>
    <ul class="entries">
      <li v-for="habitEntry in habitEntriesSorted" :key="habitEntry.id">
        {{ formatTime(habitEntry.createdAt) }}:
        {{ habitEntry.name }}
      </li>
    </ul>
  </loading-box>
</template>

<script>
import { DateTime } from "luxon";
import * as lodash from "lodash";

export default {
  emits: ["habit-created"],
  data() {
    return {
      habits: [],
      habitEntries: [],
      refresh: 0,
    };
  },

  computed: {
    apiUrls() {
      return [
        "/api/db/list/habits?deprecated=0",
        "/api/db/list/habit_entries?__no_get_related&date=" +
          this.todayAdjusted().toISODate(),
      ];
    },

    habitsSorted() {
      return lodash.orderBy(this.habits, ["points", "name"], ["desc", "asc"]);
    },

    habitEntriesSorted() {
      return lodash.orderBy(this.habitEntries, ["createdAt"], ["desc"]);
    },
  },

  methods: {
    formatTime(timestamp) {
      return DateTime.fromSeconds(timestamp).toLocaleString(
        DateTime.TIME_SIMPLE
      );
    },

    onClick(habit) {
      this.$apiPost("/api/db/create/habit_entries", {
        date: this.todayAdjusted().toISODate(),
        habit: habit.id,
        name: habit.name,
        points: habit.points,
      }).then((habit) => {
        this.refresh++;
        this.$emit("habit-created", habit);
      });
    },

    onDataLoaded(data) {
      this.habits = data[0];
      this.habitEntries = data[1];
    },
  },
};
</script>

<style scoped>
.badges {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.entries {
  margin-top: 10px;
  font-size: 0.8rem;
}
</style>
