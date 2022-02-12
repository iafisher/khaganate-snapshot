<template>
  <b-form @submit.prevent="onSubmit">
    <div v-if="submitting" class="text-center">
      <b-spinner />
    </div>

    <b-form-group label="Title" label-for="input-title">
      <b-form-input
        id="input-title"
        v-model="form.title"
        type="text"
        required
      />
    </b-form-group>

    <b-form-group label="Description" label-for="input-description">
      <b-textarea id="input-description" v-model="form.description" rows="8" />
    </b-form-group>

    <b-form-group label="Deadline" label-for="input-deadline">
      <b-form-input id="input-deadline" v-model="form.deadline" type="date" />
    </b-form-group>

    <b-form-group label="Priority" label-for="input-priority">
      <b-radio-group
        id="input-priority"
        v-model="form.priority"
        :options="priorityOptions"
      />
    </b-form-group>

    <b-form-group label="Status" label-for="input-status">
      <b-radio-group
        id="input-status"
        v-model="form.status"
        :options="statusOptions"
      />
    </b-form-group>

    <div class="text-center">
      <b-button type="submit" variant="primary">Submit</b-button>
    </div>
  </b-form>
</template>

<script>
import * as taskService from "services/task_service.js";

export default {
  props: {
    task: { type: Object, required: false, default: null },
  },
  emits: ["form-submitted"],

  data() {
    let form;
    if (this.task === null) {
      form = {
        id: null,
        title: "",
        description: "",
        deadline: null,
        status: "open",
        priority: 2,
      };
    } else {
      form = {
        id: this.task.id,
        title: this.task.title,
        description: this.task.description,
        deadline: this.task.deadline,
        status: this.task.status,
        priority: this.task.priority,
      };
    }

    return {
      form,
      priorityOptions: [
        { text: "P0", value: 0 },
        { text: "P1", value: 1 },
        { text: "P2", value: 2 },
        { text: "P3", value: 3 },
        { text: "P4", value: 4 },
      ],
      statusOptions: [
        { text: "open", value: "open" },
        { text: "fixed", value: "fixed" },
        { text: "won't fix", value: "wontfix" },
        { text: "obsolete", value: "obsolete" },
        { text: "duplicate", value: "duplicate" },
      ],
      submitting: false,
    };
  },

  methods: {
    onSubmit() {
      this.submitting = true;
      if (this.form.id !== null) {
        taskService.updateTask(this.form).then((updatedTask) => {
          this.submitting = false;
          this.$popup(
            `Updated task '${updatedTask.title}' (${updatedTask.id}).`,
            {
              autoDismiss: true,
            }
          );
          this.$emit("form-submitted", updatedTask);
        });
      } else {
        taskService.createTask(this.form).then((newTask) => {
          this.submitting = false;
          this.$popup(`Created task '${newTask.title}' (${newTask.id}).`, {
            autoDismiss: true,
          });
          this.$emit("form-submitted", newTask);
        });
      }
    },
  },
};
</script>
