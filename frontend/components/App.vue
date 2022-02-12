<template>
  <div class="app">
    <b-navbar class="mb-3" type="dark" variant="info">
      <b-navbar-brand :to="{ name: 'home' }">Khaganate</b-navbar-brand>

      <b-navbar-nav>
        <b-nav-item :to="{ name: 'biblio-home' }">biblio</b-nav-item>
        <b-nav-item-dropdown text="books">
          <b-dropdown-item :to="{ name: 'books-month', params: urlParams }">
            reading log
          </b-dropdown-item>
          <b-dropdown-item :to="{ name: 'books' }">
            all-time reading log
          </b-dropdown-item>
          <b-dropdown-item :to="{ name: 'books-to-read' }">
            to-read list
          </b-dropdown-item>
        </b-nav-item-dropdown>
        <b-nav-item :to="{ name: 'calendar-today' }">calendar</b-nav-item>
        <b-nav-item :to="{ name: 'file-home' }">files</b-nav-item>
        <b-nav-item-dropdown text="films">
          <b-dropdown-item :to="{ name: 'films', params: { year } }">
            film log
          </b-dropdown-item>
          <b-dropdown-item :to="{ name: 'films-to-watch' }">
            to-watch list
          </b-dropdown-item>
        </b-nav-item-dropdown>
        <b-nav-item :to="{ name: 'finances-month', params: urlParams }">
          finances
        </b-nav-item>
        <b-nav-item :to="{ name: 'goals-month', params: urlParams }">
          goals
        </b-nav-item>
        <b-nav-item :to="{ name: 'journal-home' }">journal</b-nav-item>
        <b-nav-item :to="{ name: 'metrics-month', params: urlParams }">
          metrics
        </b-nav-item>
        <b-nav-item :to="{ name: 'tasks' }">tasks</b-nav-item>
        <b-nav-item :to="{ name: 'travel' }">travel</b-nav-item>
      </b-navbar-nav>

      <b-navbar-nav class="ml-auto">
        <b-nav-form @submit.prevent="onSearchBoxSubmit">
          <b-form-input
            v-model.trim="searchQuery"
            type="text"
            placeholder="search"
          />
        </b-nav-form>
      </b-navbar-nav>
    </b-navbar>

    <!-- eslint-disable-next-line vue/require-v-for-key -->
    <div v-for="alert in alerts" :class="['alert', 'alert-' + alert.level]">
      {{ alert.message }}
    </div>

    <router-view />
  </div>
</template>

<script>
import { DateTime } from "luxon";

export default {
  data() {
    return {
      alerts: [],
      searchQuery: "",
    };
  },

  computed: {
    currentDate() {
      return DateTime.local();
    },

    year() {
      return this.currentDate.year;
    },

    urlParams() {
      return { year: this.currentDate.year, month: this.currentDate.month };
    },
  },

  created() {
    this.fetchAlerts();

    const fiveMinutesInMs = 5 * 60 * 1000;
    setInterval(this.fetchAlerts, fiveMinutesInMs);
  },

  methods: {
    fetchAlerts() {
      this.$apiGet("/api/alerts/list").then((alerts) => {
        this.alerts = alerts;
      });
    },

    onSearchBoxSubmit() {
      this.$router.push({
        name: "search-results",
        params: { query: this.searchQuery },
      });
    },
  },
};
</script>

<style scoped>
.alert {
  width: 95%;
  margin: 0 auto;
  border: 1px solid black;
  text-align: center;
  margin-bottom: 1.5rem;
}

.alert-info {
  background-color: lightyellow;
}

.alert-severe {
  background-color: #ffe4e4;
}
</style>
