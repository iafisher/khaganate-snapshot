<template>
  <div class="page-wide">
    <task-box
      v-if="task !== null"
      :task="task"
      :standalone="true"
      @task-updated="refreshTask"
      @comment-created="refreshTask"
    />
  </div>
</template>

<script>
import * as taskService from "services/task_service.js";
import TaskBox from "./TaskBox.vue";

export default {
  components: {
    TaskBox,
  },
  props: {
    id: { type: Number, required: true },
  },

  data() {
    return { task: null };
  },

  watch: {
    $route() {
      this.refreshTask();
    },
  },

  created() {
    this.refreshTask();
  },

  methods: {
    refreshTask() {
      taskService.getTask(this.id).then((task) => {
        this.task = task;
        document.title = this.task.title + " | Khaganate";
      });
    },
  },
};
</script>
