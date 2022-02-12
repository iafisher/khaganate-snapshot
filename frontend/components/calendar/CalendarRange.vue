<template>
  <b-overlay :show="loading">
    <div v-if="!loading" class="calendar-box">
      <div v-for="(iterDate, i) in dates" :key="iterDate.toISODate()">
        <h5 class="text-center">
          {{ iterDate.toFormat("ccc LLL d") }}
        </h5>
        <calendar-day
          :events="eventsByDay[i]"
          :all-day-events="allDayEventsByDay[i]"
          :max-all-day-events="maxAllDayEvents"
          :current-time="iterDate.hasSame(today(), 'day') ? now : null"
          @event-updated="fetchData"
          @event-deleted="fetchData"
        />
      </div>
    </div>
  </b-overlay>
</template>

<script>
import { DateTime } from "luxon";

import CalendarDay from "./CalendarDay.vue";

export default {
  components: {
    CalendarDay,
  },
  props: {
    start: { type: Object, required: true },
    end: { type: Object, required: true },
    refresh: { type: Number, required: false, default: 0 },
  },

  data() {
    return { events: [], loading: false, now: DateTime.local() };
  },

  computed: {
    dates() {
      const dates = [];
      let iterDate = this.start;
      while (iterDate <= this.end) {
        dates.push(iterDate);
        iterDate = iterDate.plus({ days: 1 });
      }
      return dates;
    },

    eventsByDay() {
      const eventsByDay = [];
      for (const date of this.dates) {
        const dateAsIso = date.toISODate();
        eventsByDay.push(
          this.events.filter(
            (event) => event.start !== null && event.startDate === dateAsIso
          )
        );
      }
      return eventsByDay;
    },

    allDayEventsByDay() {
      const eventsByDay = [];
      for (const date of this.dates) {
        const dateAsIso = date.toISODate();
        eventsByDay.push(
          this.events.filter(
            (event) =>
              event.start === null &&
              event.startDate <= dateAsIso &&
              dateAsIso <= event.endDate
          )
        );
      }
      return eventsByDay;
    },

    maxAllDayEvents() {
      let max = 0;
      for (const allDayEvents of this.allDayEventsByDay) {
        max = Math.max(max, allDayEvents.length);
      }
      return max;
    },
  },

  watch: {
    refresh() {
      this.fetchData();
    },
  },

  created() {
    this.fetchData();

    const oneMinuteInMs = 60 * 1000;
    setInterval(() => {
      this.now = DateTime.local();
    }, oneMinuteInMs);
  },

  methods: {
    fetchData() {
      const start = this.start.toISODate();
      const end = this.end.toISODate();
      const url = `/api/calendar/events/list/${start}/${end}`;
      this.loading = true;
      this.$apiGet(url).then((events) => {
        this.loading = false;
        this.events = events;
      });
    },

    onEventDeleted(dayIndex, deletedEvent) {
      for (let i = 0; i < this.events.length; i++) {
        const event = this.events[i];
        if (event.id === deletedEvent.id) {
          this.events.splice(i, 1);
        }
      }
    },

    onEventUpdated(dayIndex, updatedEvent) {
      for (let i = 0; i < this.events.length; i++) {
        const event = this.events[i];
        if (event.id === updatedEvent.id) {
          this.events.splice(i, 1, updatedEvent);
        }
      }
    },
  },
};
</script>

<style scoped>
.calendar-box {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
}

h5 {
  font-size: 1rem;
}
</style>
