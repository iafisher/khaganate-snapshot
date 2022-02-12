<template>
  <loading-box class="page-wide" :url="apiUrl" @data-loaded="onDataLoaded">
    <h1>{{ dateAsString }}</h1>
    <div class="nav">
      <date-link :date="date.minus({ days: 1 })"> &lt; yesterday </date-link>
      <router-link :to="{ name: 'journal-month', params: { year, month } }">
        this month
      </router-link>
      <date-link :date="date.plus({ days: 1 })">tomorrow &gt;</date-link>
    </div>

    <template v-if="inFuture">
      <p class="text-center">This date is in the future.</p>
    </template>
    <template v-else>
      <h2>Journal</h2>
      <markdown-block v-if="entry" class="mb-3" :text="entry" />
      <p v-else>No journal entry for this date.</p>

      <h2>Calendar</h2>
      <calendar-range
        class="calendar"
        :start="date.minus({ days: 1 })"
        :end="date.plus({ days: 1 })"
      />

      <template v-if="bookEntries.length > 0">
        <h2>
          <router-link :to="{ name: 'books-month', params: { year, month } }">
            Reading
          </router-link>
        </h2>
        <ul>
          <li v-for="bookEntry in bookEntries" :key="bookEntry.id">
            <cite>{{ bookEntry.book.title }}</cite> ({{
              bookEntry.book.authors
            }}), started
            <date-link :date="bookEntry.dateStarted">
              {{ getDateDifference(bookEntry.dateStarted) }}
            </date-link>
            <template v-if="bookEntry.dateEnded">
              and finished
              <date-link :date="bookEntry.dateEnded">
                {{ getDateDifference(bookEntry.dateEnded) }}
              </date-link>
            </template>
          </li>
        </ul>
      </template>

      <template v-if="credits.length > 0">
        <h2>
          <router-link
            :to="{ name: 'finances-month', params: { year, month } }"
          >
            Credits
          </router-link>
        </h2>
        <credits-table :credits="credits" :links-to-month-pages="true" />
      </template>
    </template>
  </loading-box>
</template>

<script>
import { DateTime } from "luxon";

import CalendarRange from "components/calendar/CalendarRange.vue";
import CreditsTable from "components/finances/CreditsTable.vue";

export default {
  components: {
    CalendarRange,
    CreditsTable,
  },
  props: {
    year: { type: Number, required: true },
    month: { type: Number, required: true },
    day: { type: Number, required: true },
  },

  data() {
    return {
      bookEntries: [],
      credits: [],
      entry: "",
    };
  },

  computed: {
    apiUrl() {
      return `/api/journal/entries/${this.year}/${this.month}/${this.day}`;
    },

    date() {
      return DateTime.fromObject({
        year: this.year,
        month: this.month,
        day: this.day,
      });
    },

    dateAsString() {
      return this.date.toFormat("cccc, d LLLL y");
    },

    dateAsISO() {
      return this.date.toISODate();
    },

    inFuture() {
      return this.date.startOf("day") > DateTime.local();
    },
  },

  methods: {
    onDataLoaded(data) {
      this.bookEntries = data.bookEntries;
      this.entry = data.entry;
      this.events = data.events;
      this.credits = data.credits;
    },

    getDateDifference(date) {
      const dateObject = DateTime.fromISO(date);
      if (this.date.equals(dateObject)) {
        return "today";
      }

      let difference, modifier;
      if (this.date < dateObject) {
        difference = Math.ceil(dateObject.diff(this.date).as("days"));
        modifier = "later";
      } else {
        difference = Math.ceil(this.date.diff(dateObject).as("days"));
        modifier = "ago";
      }

      return (
        difference + " " + (difference === 1 ? "day" : "days") + " " + modifier
      );
    },
  },
};
</script>

<style scoped>
.nav,
.info,
.calendar {
  margin-bottom: 1rem;
}

.nav {
  width: 350px;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.info {
  font-size: 0.8rem;
}

.info td:first-child {
  font-weight: bold;
  padding-right: 10px;
}

.written-journal >>> li p {
  margin-bottom: 0;
}
</style>
