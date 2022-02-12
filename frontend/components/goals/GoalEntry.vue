<template>
  <div>
    <template v-if="goal.progressFromTask">
      <router-link
        :to="{ name: 'task', params: { id: goal.progressFromTask } }"
        target="_blank"
      >
        {{ goal.title }}
      </router-link>
    </template>
    <template v-else>
      {{ goal.title }}
    </template>

    <template v-if="!goal.autoProgress">
      <span class="progress-btn" @click="updateProgress(goal, 1)">(+)</span>
      <span class="progress-btn" @click="updateProgress(goal, -1)">(-)</span>
    </template>
    <b-progress
      v-if="goal.autoProgress && goal.metricIsMaximum"
      :max="goal.maxProgress"
    >
      <b-progress-bar
        :variant="goal.progress < goal.maxProgress ? 'warning' : 'danger'"
        :value="goal.progress"
        :label="'' + goal.progress"
      ></b-progress-bar>
      <b-progress-bar
        variant="primary"
        :value="goal.maxProgress - goal.progress"
      ></b-progress-bar>
    </b-progress>
    <b-progress v-else :max="goal.maxProgress">
      <b-progress-bar
        :variant="goal.progress >= goal.maxProgress ? 'success' : 'primary'"
        :value="goal.progress"
        :label="'' + goal.progress"
      ></b-progress-bar>
    </b-progress>
  </div>
</template>

<script>
export default {
  props: {
    goal: { type: Object, required: true },
  },
  emits: ["goal-progress-updated"],

  methods: {
    updateProgress(goal, amount) {
      const newProgress = goal.progress + amount;
      if (newProgress < 0 || newProgress > goal.maxProgress) {
        return;
      }

      this.$emit("goal-progress-updated", { goal, amount });
    },
  },
};
</script>

<style scoped>
.progress-btn {
  font-size: 0.8rem;
  cursor: pointer;
}
</style>
