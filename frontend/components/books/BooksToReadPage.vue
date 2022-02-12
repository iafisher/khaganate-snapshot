<template>
  <loading-box
    class="page-wider"
    url="/api/db/list/book-recommendations?date_removed__null"
    @data-loaded="onDataLoaded"
  >
    <h1>
      <strong>
        {{ recommendations.length | pluralize("book") }}
      </strong>
      on reading list
    </h1>

    <b-input
      v-model="searchFilter"
      class="search"
      placeholder="Search (enter at least 3 characters)"
    />

    <b-table
      striped
      hover
      outlined
      :fields="fields"
      :items="filteredRecommendations"
      sort-by="title"
    >
      <template #cell(title)="data">
        <cite>{{ data.value }}</cite>
      </template>

      <template #cell(pitch)="data">
        <markdown-inline :text="data.value" />
      </template>

      <template #cell(dateAdded)="data">
        <date-link v-if="data.value" :date="data.value" />
      </template>

      <template #cell(button)="data">
        <b-button
          variant="primary"
          size="sm"
          @click="
            modalRecommendation = data.item;
            $bvModal.show('start-book-modal');
          "
        >
          start
        </b-button>
      </template>
    </b-table>

    <modal-form
      id="start-book-modal"
      :url="formUrl"
      :fields="formFields"
      @form-submitted="onStartBook($event)"
    >
      <template #title>
        Start <cite>{{ modalRecommendation.title }}</cite>
      </template>
    </modal-form>
  </loading-box>
</template>

<script>
export default {
  data() {
    return {
      fields: [
        { key: "title", label: "title", sortable: true },
        { key: "authors", label: "author", sortable: true },
        { key: "pitch", label: "pitch" },
        { key: "dateAdded", label: "date added", sortable: true },
        { key: "button", label: "" },
      ],
      formFields: [
        {
          label: "Date started",
          key: "dateStarted",
          type: "date",
          initial: this.todayAdjusted().toISODate(),
        },
      ],
      modalRecommendation: null,
      recommendations: [],
      searchFilter: "",
    };
  },

  computed: {
    filteredRecommendations() {
      if (this.searchFilter.length < 3) {
        return this.recommendations;
      }

      const q = this.searchFilter.toLowerCase();
      return this.recommendations.filter(
        (rec) =>
          rec.title.toLowerCase().includes(q) ||
          rec.authors.toLowerCase().includes(q)
      );
    },

    formUrl() {
      if (this.modalRecommendation) {
        return (
          "/api/books/recommendations/start/" + this.modalRecommendation.id
        );
      } else {
        return "";
      }
    },
  },

  methods: {
    onDataLoaded(data) {
      this.recommendations = data;
      this.recommendations.forEach((recommendation) => {
        recommendation.title = recommendation.book.title;
        recommendation.authors = recommendation.book.authors;
      });
    },

    onStartBook(entry) {
      for (let i = 0; i < this.recommendations.length; i++) {
        const recommendation = this.recommendations[i];
        if (recommendation.book.id === entry.bookId) {
          this.recommendations.splice(i, 1);
          return;
        }
      }

      console.error(`Could not find book with ID of ${entry.bookId}.`);
    },
  },
};
</script>

<style scoped>
table {
  margin-top: 20px;
  font-size: 0.9rem;
}

.search {
  max-width: 400px;
}
</style>
