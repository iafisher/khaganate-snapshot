<template>
  <loading-box
    class="page-very-wide"
    :url="apiUrl"
    :refresh="refresh"
    @data-loaded="onDataLoaded"
  >
    <b-row>
      <h1>
        <strong>{{ films.length | pluralize("film") }}</strong> seen<span
          v-if="films.length !== uniqueFilmsCount"
        >
          ({{ uniqueFilmsCount }} unique)</span
        >,
        {{ year || "all time" }}
      </h1>
      <b-icon
        class="new-film"
        icon="plus"
        @click="$bvModal.show('new-film-modal')"
      ></b-icon>
    </b-row>
    <b-row class="controls">
      <b-input
        v-model="searchFilter"
        placeholder="Search (enter at least 3 characters)"
      />

      <div>
        <span class="mr-3">
          <template v-if="yearOrDefault > earliest.year">
            <router-link
              :to="{
                name: 'films',
                params: { year: yearOrDefault - 1 },
              }"
            >
              &lt; {{ yearOrDefault - 1 }}
            </router-link>
          </template>
          <template v-else>&lt; {{ yearOrDefault - 1 }}</template>
        </span>

        <span>
          <router-link v-if="year" :to="{ name: 'films' }"
            >all-time</router-link
          >
          <router-link
            v-else
            :to="{
              name: 'films',
              params: { year: currentDate.year },
            }"
            >{{ currentDate.year }}</router-link
          >
        </span>

        <span class="ml-3">
          <template v-if="yearOrDefault < currentDate.year">
            <router-link
              :to="{
                name: 'films',
                params: { year: yearOrDefault + 1 },
              }"
            >
              {{ yearOrDefault + 1 }} &gt;
            </router-link>
          </template>
          <template v-else>{{ yearOrDefault + 1 }} &gt;</template>
        </span>
      </div>
    </b-row>

    <b-table
      striped
      hover
      outlined
      :fields="fields"
      :items="filteredFilms"
      sort-by="dateViewed"
      :sort-desc="year ? false : true"
    >
      <template #cell(title)="data">
        <a v-if="data.item.film.kgLink" :href="data.item.film.kgLink">
          {{ data.value }}
        </a>
        <template v-else>
          {{ data.value }}
        </template>
      </template>

      <template #cell(dateViewed)="data">
        <date-link v-if="data.value" :date="data.value" />
      </template>

      <template #cell(rating)="data">
        <b-icon
          v-for="i in getNumberOfFullStars(data.value)"
          :key="i"
          icon="star-fill"
        /><b-icon v-if="hasHalfStar(data.value)" icon="star-half" />
      </template>
    </b-table>

    <modal-form
      id="new-film-modal"
      url="/api/films/watch"
      title="New film"
      :fields="newFilmFields"
      @form-submitted="refresh++"
    />
  </loading-box>
</template>

<script>
import { DateTime } from "luxon";

export default {
  props: {
    year: { type: Number, required: false, default: null },
  },

  data() {
    return {
      earliest: DateTime.fromObject({ year: 2022 }),
      fields: [
        {
          key: "title",
          label: "title",
          sortable: true,
          tdClass: "font-italic",
        },
        { key: "directors", label: "director", sortable: true },
        { key: "year", label: "year", sortable: true },
        { key: "language", label: "language", sortable: true },
        { key: "dateViewed", label: "date", sortable: true },
        { key: "rating", label: "rating", tdClass: "rating", sortable: true },
        { key: "documentary", label: "documentary?", sortable: true },
        { key: "synopsis", label: "synopsis" },
      ],
      films: [],
      newFilmFields: [
        {
          label: "Title",
          key: "title",
          type: "text",
          required: true,
          description:
            "Rewatches will automatically be de-duped based on the title, director, and year of the film.",
        },
        { label: "Director", key: "directors", type: "text", required: true },
        { label: "Year", key: "year", type: "number", required: false },
        { label: "Language", key: "language", type: "text", required: true },
        {
          label: "Date viewed",
          key: "dateViewed",
          type: "date",
          required: true,
          initial: this.todayAdjusted().toISODate(),
        },
        {
          label: "Rating",
          key: "rating",
          type: "number",
          min: 1,
          max: 5,
          step: 0.5,
        },
        { label: "Documentary", key: "documentary", type: "checkbox" },
        { label: "Synopsis", key: "synopsis", type: "text", required: false },
        {
          label: "Notes",
          key: "notes",
          type: "text",
          required: false,
          description: "e.g., 'Saw in theaters'",
        },
      ],
      refresh: 0,
      searchFilter: "",
    };
  },

  computed: {
    apiUrl() {
      const queryString =
        this.year === null ? "" : `?date_viewed__startswith=${this.year}`;
      return "/api/db/list/film-entries" + queryString;
    },

    currentDate() {
      return DateTime.local();
    },

    filteredFilms() {
      if (this.searchFilter.length < 3) {
        return this.films;
      } else {
        const q = this.searchFilter.toLowerCase();
        return this.films.filter(
          (film) =>
            film.title.toLowerCase().includes(q) ||
            film.directors.toLowerCase().includes(q) ||
            film.synopsis.toLowerCase().includes(q)
        );
      }
    },

    uniqueFilmsCount() {
      const filmSet = new Set();
      for (const film of this.films) {
        filmSet.add(film.film.id);
      }
      return filmSet.size;
    },

    yearOrDefault() {
      return this.year === null ? this.currentDate.year : this.year;
    },
  },

  methods: {
    onDataLoaded(data) {
      this.films = data;
      this.films.forEach((entry) => {
        entry.title = entry.film.title;
        entry.directors = entry.film.directors;
        entry.year = entry.film.year;
        entry.language = entry.film.language;
        entry.documentary = entry.film.documentary;
        entry.synopsis = entry.film.synopsis;
      });
    },

    getNumberOfFullStars(rating) {
      return rating ? Math.floor(parseFloat(rating)) : 0;
    },

    hasHalfStar(rating) {
      return rating
        ? Math.floor(parseFloat(rating)) !== parseFloat(rating)
        : false;
    },
  },
};
</script>

<style scoped>
.row {
  margin: 0;
}

.new-film {
  margin-left: auto;
  font-size: 3rem;
  cursor: pointer;
}

.controls {
  align-items: baseline;
  justify-content: space-between;
}

.controls input[type="text"] {
  max-width: 400px;
}

table {
  margin-top: 1rem;
  font-size: 0.9rem;
}

table >>> td.rating {
  white-space: nowrap;
}
</style>
