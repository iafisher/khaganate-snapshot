<template>
  <div>
    <b-overlay :show="loading">
      <div class="top-row">
        <h2>
          <!-- eslint-disable vue/multiline-html-element-content-newline -->
          <router-link :to="{ name: 'tasks' }" target="_blank"
            >Tasks</router-link
          >
          <!-- eslint-enable vue/multiline-html-element-content-newline -->
        </h2>

        <b-dropdown size="lg" variant="outline">
          <template #button-content>
            <b-icon icon="plus"></b-icon>
          </template>
          <b-dropdown-item @click="$bvModal.show('new-task-modal')">
            New task
          </b-dropdown-item>
          <b-dropdown-item @click="$bvModal.show('new-time-slot-modal')">
            New time slot
          </b-dropdown-item>
        </b-dropdown>
      </div>
    </b-overlay>

    <b-overlay :show="refreshing">
      <task-box
        v-for="task in taskGroups[0]"
        :key="task.id"
        :task="task"
        @task-updated="
          setTask(task.id, $event);
          $emit('task-updated', $event);
        "
        @comment-created="refreshTask(task.id)"
        @time-slot-created="refreshTask(task.id)"
        @task-deadline-updated="setTask(task.id, $event)"
      />
      <hr v-if="taskGroups[0].length > 0 && taskGroups[1].length > 0" />
      <task-box
        v-for="task in taskGroups[1]"
        :key="task.id"
        :task="task"
        @task-updated="
          setTask(task.id, $event);
          $emit('task-updated', $event);
        "
        @comment-created="refreshTask(task.id)"
        @time-slot-created="refreshTask(task.id)"
        @task-deadline-updated="setTask(task.id, $event)"
      />

      <b-form inline>
        <b-form-input
          v-model="newTaskForm.title"
          required
          placeholder="Title"
        ></b-form-input>
        <b-form-select
          v-model="newTaskForm.priority"
          class="ml-1"
          :options="priorityOptions"
          required
        ></b-form-select>
        <b-form-input
          v-model="newTaskForm.deadline"
          class="ml-1"
          type="date"
        ></b-form-input>
        <b-button
          class="ml-1"
          size="sm"
          variant="primary"
          :disabled="!newTaskForm.title"
          @click="onNewTaskSubmitted"
        >
          Create
        </b-button>
      </b-form>

      <template v-if="taskGroups[2].length > 0">
        <hr />
        <details>
          <summary>On deck</summary>
          <task-box
            v-for="task in taskGroups[2]"
            :key="task.id"
            :task="task"
            @task-updated="
              setTask(task.id, $event);
              $emit('task-updated', $event);
            "
            @comment-created="refreshTask(task.id)"
            @time-slot-created="refreshTask(task.id)"
            @task-deadline-updated="setTask(task.id, $event)"
          />
        </details>
      </template>
    </b-overlay>

    <b-modal id="new-task-modal" size="lg" :ok-disabled="true" title="New task">
      <template #default="{ ok }">
        <task-form
          @form-submitted="
            ok();
            onTaskCreated($event);
          "
        />
      </template>

      <template #modal-footer>
        <span></span>
      </template>
    </b-modal>
  </div>
</template>

<script>
import * as lodash from "lodash";
import { DateTime } from "luxon";

import * as taskService from "services/task_service.js";
import TaskForm from "./TaskForm.vue";
import TaskBox from "./TaskBox.vue";
import { isOpen } from "./tasks.js";

function newTaskFormDefaults() {
  return {
    title: "",
    priority: 1,
    deadline: null,
  };
}

export default {
  components: {
    TaskBox,
    TaskForm,
  },
  emits: ["task-updated"],

  data() {
    return {
      loading: false,
      newTaskForm: newTaskFormDefaults(),
      priorityOptions: [
        { text: "P0", value: 0 },
        { text: "P1", value: 1 },
        { text: "P2", value: 2 },
        { text: "P3", value: 3 },
        { text: "P4", value: 4 },
      ],
      refreshing: false,
      search: "",
      tasks: [],
    };
  },

  computed: {
    searchedTasks() {
      if (this.search.length < 3) {
        return [];
      }

      const searchLowerCase = this.search.toLowerCase();
      const tasks = this.tasks.filter(
        (task) =>
          isOpen(task) && task.title.toLowerCase().includes(searchLowerCase)
      );
      return lodash.orderBy(tasks, ["title"]);
    },

    taskGroups() {
      const groups = [[], [], []];
      for (const task of this.tasks) {
        if (!isOpen(task)) {
          continue;
        }

        const daysFromDeadline =
          task.deadline !== null
            ? DateTime.fromISO(task.deadline).diff(this.todayAdjusted(), "days")
                .days
            : null;

        if (
          task.priority === 0 ||
          (daysFromDeadline !== null && daysFromDeadline <= 3)
        ) {
          groups[0].push(task);
        } else if (
          task.priority === 1 ||
          (daysFromDeadline !== null && daysFromDeadline <= 7)
        ) {
          groups[1].push(task);
        } else if (task.priority === 2) {
          groups[2].push(task);
        }
      }

      return groups;
    },
  },

  created() {
    this.loading = true;
    taskService.getTasks().then((tasks) => {
      this.loading = false;
      this.tasks = tasks;
    });
  },

  methods: {
    refreshTask(taskId) {
      this.refreshing = true;
      taskService.getTask(taskId).then((updatedTask) => {
        this.refreshing = false;
        this.setTask(taskId, updatedTask);
      });
    },

    onNewTaskSubmitted() {
      this.refreshing = true;
      taskService.createTask(this.newTaskForm).then((newTask) => {
        this.refreshing = false;
        this.newTaskForm = newTaskFormDefaults();
        this.tasks.push(newTask);
      });
    },

    onTaskCreated(task) {
      this.tasks.push(task);
    },

    onTimeSlotCreated(timeSlot) {
      this.refreshTask(timeSlot.task.id);
    },

    setTask(taskId, updatedTask) {
      for (let i = 0; i < this.tasks.length; i++) {
        const task = this.tasks[i];
        if (task.id === taskId) {
          this.tasks.splice(i, 1, updatedTask);
          return;
        }
      }

      console.error(`Could not find task with ID of ${taskId}.`);
    },
  },
};
</script>

<style scoped>
.top-row {
  display: flex;
  flex-direction: row;
  align-items: baseline;
  margin-bottom: 10px;
}

.top-row a {
  color: initial;
  text-decoration: underline;
}

.top-row .b-dropdown {
  margin-left: auto;
}

.radio {
  margin-bottom: 10px;
}

.controls {
  display: flex;
  flex-direction: row;
  gap: 20px;
}

h3,
input {
  margin: 16px 0;
}
</style>
