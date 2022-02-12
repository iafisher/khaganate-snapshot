<template>
  <loading-box
    class="page-very-wide"
    :url="apiUrl"
    :refresh="refresh"
    @data-loaded="books = $event"
  >
    <b-row>
      <h1>
        <strong>{{ filteredBooksValue.toFixed(1) | pluralize("book") }}</strong>
        <template v-if="totalPageCount !== null">
          ({{ totalPageCount | commas | pluralize("page") }})
        </template>
        read,
        <template v-if="month">
          {{ monthName }}
          <router-link :to="{ name: 'books-year', params: { year } }">
            {{ year }}
          </router-link>
        </template>
        <template v-else-if="year">
          {{ year }}
        </template>
        <template v-else>all-time</template>
      </h1>
      <b-icon
        class="new-book"
        icon="plus"
        @click="$bvModal.show('start-book-modal')"
      ></b-icon>
    </b-row>

    <b-row class="controls">
      <b-input
        v-model="searchFilter"
        placeholder="Search (enter at least 3 characters)"
      />

      <b-form-checkbox v-model="showAbandoned">
        Show abandoned books
      </b-form-checkbox>

      <div class="nav">
        <month-nav
          v-if="year"
          :year="year"
          :month="month"
          :earliest="earliest"
          url="books-month"
          year-url="books-year"
        />
        <month-nav
          v-else
          :year="currentDate.year"
          :earliest="earliest"
          url="books-month"
          year-url="books-year"
        />
      </div>
    </b-row>

    <b-table
      striped
      hover
      outlined
      :fields="fields"
      :items="filteredBooks"
      sort-by="dateStarted"
    >
      <template #cell(title)="data">
        <a v-if="data.item.kgLink" :href="data.item.kgLink">
          {{ data.value }}
        </a>
        <template v-else>
          {{ data.value }}
        </template>
      </template>

      <template #cell(dateStarted)="data">
        <date-link :date="data.value" />
      </template>

      <template #cell(dateEnded)="data">
        <date-link v-if="data.value" :date="data.value" />
      </template>

      <template #cell(valueInInterval)="data">
        {{ data.value ? data.value.toFixed(1) : "" }}
        <template v-if="data.item.skimmed">(skimmed)</template>
      </template>

      <template #cell(rating)="data">
        <b-icon
          v-for="i in getNumberOfFullStars(data.value)"
          :key="i"
          icon="star-fill"
        /><b-icon v-if="hasHalfStar(data.value)" icon="star-half" />
      </template>

      <template #cell(button)="data">
        <b-button
          v-if="!data.item.dateEnded"
          variant="primary"
          size="sm"
          @click="
            modalEntry = data.item;
            $bvModal.show('finish-book-modal');
          "
        >
          finish
        </b-button>
      </template>
    </b-table>

    <modal-form
      id="finish-book-modal"
      :url="finishBookUrl"
      :fields="finishBookFields"
      :data="modalEntry"
      @form-submitted="refresh++"
    >
      <template #title>
        Finish <cite>{{ modalEntry.title }}</cite>
      </template>
    </modal-form>

    <modal-form
      id="start-book-modal"
      title="Start book"
      url="/api/books/start"
      :fields="startBookFields"
      @form-submitted="refresh++"
    />
  </loading-box>
</template>

<script>
import * as lodash from "lodash";
import { DateTime } from "luxon";

import { getMonthName } from "common.js";

export default {
  props: {
    year: { type: Number, default: null },
    month: { type: Number, default: null },
  },

  data() {
    return {
      books: [],
      earliest: DateTime.local(2022, 2, 1),
      fields: [
        { key: "index", label: "" },
        {
          key: "title",
          label: "title",
          sortable: true,
          tdClass: "font-italic",
        },
        { key: "authors", label: "author", sortable: true },
        { key: "dateStarted", label: "date started", sortable: true },
        { key: "dateEnded", label: "date ended", sortable: true },
        { key: "fiction", label: "fiction" },
        { key: "pages", label: "pages", sortable: true },
        { key: "valueInInterval", label: "value", sortable: true },
        { key: "rating", label: "rating", tdClass: "rating", sortable: true },
        { key: "button", label: "" },
      ],
      finishBookFields: [
        {
          label: "Date finished",
          key: "dateEnded",
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
        { label: "Pages", key: "pages", type: "number", required: false },
        { label: "Abandoned", key: "abandoned", type: "checkbox" },
        { label: "Skimmed", key: "skimmed", type: "checkbox" },
      ],
      modalEntry: null,
      refresh: 0,
      searchFilter: "",
      showAbandoned: false,
      startBookFields: [
        { label: "Title", key: "title", type: "text", required: true },
        { label: "Author", key: "authors", type: "text", required: true },
        { label: "Year", key: "year", type: "number", required: false },
        { label: "Edition", key: "edition", type: "text", required: false },
        { label: "Pages", key: "pages", type: "number", required: false },
        { label: "Fictional", key: "fictional", type: "checkbox" },
      ],
    };
  },

  computed: {
    apiUrl() {
      if (this.month) {
        return `/api/books/list/${this.year}/${this.month}`;
      } else if (this.year) {
        return `/api/books/list/${this.year}`;
      } else {
        return `/api/books/list`;
      }
    },

    finishBookUrl() {
      if (this.modalEntry) {
        return `/api/books/finish/${this.modalEntry.entryId}`;
      } else {
        return "";
      }
    },

    currentDate() {
      return DateTime.local();
    },

    monthName() {
      return this.month ? getMonthName(this.month) : "";
    },

    filteredBooks() {
      const books = [];
      let index = 1;
      const searchFilterLowerCase = this.searchFilter.toLowerCase();
      for (const book of this.books) {
        if (!book.abandoned) {
          book.index = index;
          index++;
        } else {
          if (!this.showAbandoned) {
            continue;
          }

          book._rowVariant = "danger";
        }

        if (searchFilterLowerCase.length >= 3) {
          if (
            !book.title.toLowerCase().includes(searchFilterLowerCase) &&
            !book.authors.toLowerCase().includes(searchFilterLowerCase)
          ) {
            continue;
          }
        }

        books.push(book);
      }
      return books;
    },

    filteredBooksValue() {
      return lodash.sum(
        this.filteredBooks.map((book) => {
          if (book.abandoned) {
            return 0;
          } else if (this.year) {
            return book.valueInInterval;
          } else {
            // If `this.year` is null, we are looking at the all-time reading
            // list, and `book.valueInInterval` will be blank.
            return book.value;
          }
        })
      );
    },

    totalPageCount() {
      let nPages = 0;
      let totalWithPages = 0;
      let totalWithoutPages = 0;
      for (const book of this.filteredBooks) {
        // Ignore abandoned books.
        if (book.abandoned) {
          continue;
        }

        if (book.pages) {
          nPages += book.pages * book.percentageInInterval;
          totalWithPages += 1;
        } else {
          totalWithoutPages += 1;
        }
      }

      // Ensure that at least 90% of the books have pages listed, so that the
      // count is roughly accurate.
      if (totalWithPages / (totalWithPages + totalWithoutPages) < 0.9) {
        return null;
      }

      return Math.floor(nPages);
    },
  },

  methods: {
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

.new-book {
  margin-left: auto;
  font-size: 3rem;
  cursor: pointer;
}

.controls {
  align-items: baseline;
}

.controls .nav {
  margin-left: auto;
}

.controls input[type="text"] {
  max-width: 400px;
  margin-right: 1rem;
}

div >>> td.rating {
  white-space: nowrap;
}

div >>> th {
  vertical-align: middle !important;
}

table {
  font-size: 0.9rem;
}
</style>
