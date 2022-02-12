<template>
  <loading-box
    class="page-very-wide"
    url="/api/db/list/film-recommendations"
    @data-loaded="onDataLoaded"
  >
    <h1>
      <strong>{{ recommendations.length | pluralize("film") }}</strong> to watch
    </h1>

    <b-table
      striped
      hover
      outlined
      :fields="fields"
      :items="recommendations"
      sort-by="title"
    >
      <template #cell(pitch)="data">
        <markdown-inline :text="data.value" />
      </template>

      <template #cell(dateAdded)="data">
        <date-link v-if="data.value" :date="data.value" />
      </template>
    </b-table>
  </loading-box>
</template>

<script>
export default {
  data() {
    return {
      fields: [
        {
          key: "title",
          label: "title",
          sortable: true,
          tdClass: "font-italic",
        },
        { key: "directors", label: "director(s)", sortable: true },
        { key: "documentary", label: "documentary?", sortable: true },
        { key: "pitch", label: "pitch" },
        { key: "dateAdded", label: "date", sortable: true },
      ],
      recommendations: [],
    };
  },

  methods: {
    onDataLoaded(data) {
      this.recommendations = data;
      this.recommendations.forEach((recommendation) => {
        recommendation.title = recommendation.film.title;
        recommendation.directors = recommendation.film.directors;
        recommendation.documentary = recommendation.film.documentary;
      });
    },
  },
};
</script>

<style scoped>
table {
  margin-top: 20px;
  font-size: 0.9rem;
}
</style>
