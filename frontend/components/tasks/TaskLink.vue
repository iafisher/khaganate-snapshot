<template>
  <router-link :to="{ name: 'task', params: { id: task.id } }" :target="target">
    <markdown-inline :text="task.title" :class="{ closed: !isOpen }" />
  </router-link>
</template>

<script>
import { isOpen } from "./tasks.js";

export default {
  props: {
    task: { type: Object, required: true },
    target: { type: String, required: false, default: "_self" },
  },

  computed: {
    isOpen() {
      return isOpen(this.task);
    },
  },
};
</script>

<style scoped>
.closed {
  opacity: 50%;
  text-decoration: line-through;
}
</style>
