<template>
  <b-card
    :class="cssClass"
    :header="
      'Question ' + index + ' (' + question.quiz.name + '-' + question.id + ')'
    "
    :border-variant="borderVariant"
    :header-bg-variant="headerBgVariant"
    :header-text-variant="headerTextVariant"
  >
    <b-card-text>
      <p>{{ question.text }}</p>

      <template v-if="question.type === 'short-answer'">
        <!-- SHORT ANSWER -->
        <b-input
          ref="input"
          type="text"
          :value="value ? value.response[0] : null"
          :disabled="!!result"
          @input="$emit('input', { response: [$event] })"
          @focusin="$emit('component-focused')"
        />
      </template>
      <template
        v-else-if="
          question.type === 'unordered-list' || question.type === 'ordered-list'
        "
      >
        <!-- LIST -->
        <b-input
          v-for="(_, i) in question.answer"
          :key="i"
          ref="input"
          v-model="listValues[i]"
          :disabled="!!result"
          class="list-input"
          type="text"
          @change="
            $emit('input', {
              response: listValues,
            })
          "
          @focusin="$emit('component-focused')"
        />
      </template>
      <template v-else-if="question.type === 'multiple-choice'">
        <!-- MULTIPLE CHOICE -->
        <b-form-radio-group
          v-model="radioButtonValue"
          :options="radioButtonOptions"
          :disabled="!!result"
          :name="'radio-' + question.id"
          stacked
          @change="
            $emit('input', { response: [$event] });
            $emit('component-focused');
          "
        ></b-form-radio-group>
      </template>
      <template v-else>
        <p>Error: unknown question type.</p>
      </template>

      <div v-if="result" class="mt-2">
        <p>Score: {{ result.score }} / 100</p>
        <p v-if="result.score < 100">
          Answer:
          <template
            v-if="
              question.type === 'ordered-list' ||
              question.type === 'unordered-list'
            "
          >
            <ul>
              <li v-for="answer in result.answer" :key="answer">
                {{ answer[0] }}
              </li>
            </ul>
          </template>
          <template v-else>
            {{ result.answer[0] }}
          </template>
        </p>
        <p v-if="result.score == 100">
          <b-button
            variant="primary"
            :disabled="memorized"
            @click="handleMarkMemorized"
          >
            {{ memorized ? "Memorized" : "Mark as memorized" }}
          </b-button>
        </p>
      </div>
    </b-card-text>
  </b-card>
</template>

<script>
import { isArray } from "lodash";

export default {
  props: {
    index: { type: Number, required: true },
    question: { type: Object, required: true },
    result: { type: Object, required: false, default: null },
    focused: { type: Boolean, required: true },
    value: { type: Object, required: false, default: null },
  },
  emits: ["component-focused", "input"],

  data() {
    const listValues = [];
    for (let i = 0; i < this.question.answer.length; i++) {
      listValues.push(null);
    }

    return {
      listValues,
      memorized: false,
      radioButtonValue: this.value ? this.value.response[0] : null,
    };
  },

  computed: {
    borderVariant() {
      return this.focused && !this.result ? "primary" : "secondary";
    },

    headerBgVariant() {
      if (this.result) {
        return this.result.score === 100
          ? "success"
          : this.result.score >= 66
          ? "warning"
          : "danger";
      } else {
        return this.focused && !this.result ? "primary" : "";
      }
    },

    headerTextVariant() {
      return this.focused || this.result ? "white" : "";
    },

    cssClass() {
      if (!this.focused && !this.result) {
        return ["p-0", "unfocused"];
      } else {
        return ["p-0"];
      }
    },

    radioButtonOptions() {
      const options = [];
      // Select three choices from the list. We can just take the first three
      // elements because the backend randomly shuffled them.
      for (const choice of this.question.choices.slice(0, 3)) {
        options.push({ text: choice, value: choice });
      }

      // Insert the correct answer into a random position.
      const answer = this.question.answer[randomIndex(this.question.answer)];
      options.splice(randomIndex(options), 0, { text: answer, value: answer });

      return options;
    },
  },

  watch: {
    question() {
      this.listValues = [];
      for (let i = 0; i < this.question.answer.length; i++) {
        this.listValues.push(null);
      }
    },

    value() {
      if (this.value) {
        if (this.value.length > 0) {
          this.listValues = this.value;
        }
      }
    },
  },

  mounted() {
    // Set focus to first question when quiz is opened.
    if (this.index === 1 && this.$refs.input) {
      const e = this.$refs.input;
      if (isArray(e)) {
        e[0].focus();
      } else {
        e.focus();
      }
    }
  },

  methods: {
    handleMarkMemorized() {
      this.$apiPost(`/api/db/update/quiz-questions/${this.question.id}`, {
        strength: 10,
      }).then(() => {
        this.memorized = true;
      });
    },
  },
};

function randomIndex(array) {
  return Math.floor(Math.random() * (array.length - 1));
}
</script>

<style scoped>
.unfocused {
  opacity: 50%;
}

.list-input + .list-input {
  margin-top: 5px;
}
</style>
