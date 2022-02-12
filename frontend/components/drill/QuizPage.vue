<template>
  <loading-box
    class="page-wide"
    :url="'/api/drill/get'"
    @data-loaded="onDataLoaded"
  >
    <h1 v-if="results.length > 0" class="mb-3 text-center">
      Total score: {{ (totalScore * 100).toFixed(1) }}%
    </h1>

    <div v-for="(question, i) in questions" :key="question.id">
      <quiz-question
        v-model="responses[i]"
        class="mt-2"
        :index="i + 1"
        :question="question"
        :result="results.length > 0 ? results[i] : null"
        :focused="focused === i"
        @component-focused="focused = i"
      />
    </div>

    <div v-if="!isSubmitted" class="mt-2 text-center">
      <b-button variant="primary" @click="onSubmit">Submit</b-button>
    </div>
  </loading-box>
</template>

<script>
import QuizQuestion from "./QuizQuestion.vue";

export default {
  components: {
    QuizQuestion,
  },

  data() {
    return {
      focused: null,
      questions: [],
      responses: [],
      results: [],
    };
  },

  computed: {
    isSubmitted() {
      return this.results.length > 0;
    },

    totalScore() {
      if (this.results.length === 0) {
        return null;
      }

      let points = 0;
      let possiblePoints = 0;
      for (const result of this.results) {
        points += result.score;
        possiblePoints += 100;
      }
      return points / possiblePoints;
    },
  },

  methods: {
    onBeforeUnload(event) {
      // https://developer.mozilla.org/en-US/docs/Web/API/WindowEventHandlers/onbeforeunload
      event.preventDefault();
      event.returnValue = "";
    },

    onDataLoaded(questions) {
      this.questions = questions;

      // Show an 'unsaved changes' dialog if user attempts to exit the browser
      // tab.
      window.addEventListener("beforeunload", this.onBeforeUnload);

      for (let i = 0; i < this.questions.length; i++) {
        this.responses.push(null);
      }
    },

    onSubmit() {
      const payload = [];
      for (let i = 0; i < this.questions.length; i++) {
        payload.push({
          question: this.questions[i],
          response: this.responses[i],
        });
      }

      this.$apiPost("/api/drill/submit", { responses: payload }).then(
        (results) => {
          window.removeEventListener("beforeunload", this.onBeforeUnload);
          this.results = results.results;
          window.scrollTo({ top: 0, behavior: "smooth" });
        }
      );
    },
  },
};
</script>
