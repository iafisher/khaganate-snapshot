<template>
  <div class="page-very-wide">
    <h1>
      Tasks
      <b-icon
        icon="plus"
        class="add-task-button"
        @click="$bvModal.show('new-task-modal')"
      ></b-icon>
    </h1>

    <div class="controls">
      <b-form-group label="Status">
        <b-form-checkbox-group
          v-model="statusFilter"
          :options="statusFilterOptions"
          name="status-filter"
        ></b-form-checkbox-group>
      </b-form-group>

      <b-form-group label="Priority">
        <b-form-checkbox-group
          v-model="priorityFilter"
          :options="priorityFilterOptions"
          name="priority-filter"
        ></b-form-checkbox-group>
      </b-form-group>

      <b-form-group label="Deadline">
        <b-form-checkbox-group
          v-model="deadlineFilter"
          :options="deadlineFilterOptions"
          name="deadline-filter"
        ></b-form-checkbox-group>
      </b-form-group>
    </div>

    <div class="search">
      <b-input
        v-model="searchFilter"
        placeholder="Search (enter at least 3 characters)"
      />
    </div>

    <b-overlay :show="loading">
      <b-table
        striped
        hover
        outlined
        :fields="fields"
        :items="filteredTasks"
        sort-by="priority"
      >
        <template #cell(id)="data">
          <router-link
            :to="{ name: 'task', params: { id: data.value } }"
            target="_blank"
          >
            {{ data.value }}
          </router-link>
        </template>

        <template #cell(title)="data">
          <markdown-inline :text="data.value" />
        </template>

        <template #cell(comments)="data">
          <template v-if="data.value.length > 0">
            <span class="text-nowrap">
              <b-icon icon="chat-left"></b-icon>
              {{ data.value.length }}
            </span>
          </template>
        </template>

        <template #cell(deadline)="data">
          <date-link :date="data.value" />
        </template>

        <template #cell(createdAt)="data">
          <date-link :date="data.value" />
        </template>

        <template #cell(lastUpdatedAtOverall)="data">
          <date-link :date="data.value" />
        </template>

        <template #cell(editIcon)="data">
          <b-icon
            icon="pencil-fill"
            @click="
              modalTask = data.item;
              $bvModal.show('edit-task-modal');
            "
          ></b-icon>
        </template>
      </b-table>
    </b-overlay>

    <b-modal
      id="edit-task-modal"
      size="lg"
      :ok-disabled="true"
      title="Edit task"
    >
      <template v-if="modalTask !== null" #default="{ ok }">
        <task-form
          :task="modalTask"
          @form-submitted="
            ok();
            refreshTask(modalTask.id);
          "
        />
      </template>

      <template #modal-footer>
        <span></span>
      </template>
    </b-modal>

    <b-modal id="new-task-modal" size="lg" :ok-disabled="true" title="New task">
      <template #default="{ ok }">
        <task-form
          @form-submitted="
            ok();
            tasks.push($event);
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
import * as taskService from "services/task_service.js";
import TaskForm from "./TaskForm.vue";

export default {
  components: {
    TaskForm,
  },

  data() {
    const todayPlus7 = this.todayPlusN(7);
    const todayPlus14 = this.todayPlusN(14);
    const todayPlus30 = this.todayPlusN(30);

    return {
      deadlineFilter: [todayPlus7, todayPlus14, todayPlus30, "any", null],
      deadlineFilterOptions: [
        { text: "7 days", value: todayPlus7 },
        { text: "14 days", value: todayPlus14 },
        { text: "30 days", value: todayPlus30 },
        { text: "any", value: "any" },
        { text: "none", value: null },
      ],
      fields: [
        { key: "id", label: "" },
        { key: "title", label: "title" },
        { key: "comments", label: "" },
        { key: "status", label: "status", sortable: true },
        { key: "deadline", label: "deadline", sortable: true },
        { key: "priority", label: "priority", sortable: true },
        { key: "createdAt", label: "created", sortable: true },
        { key: "lastUpdatedAtOverall", label: "last updated", sortable: true },
        { key: "editIcon", label: "" },
      ],
      loading: false,
      modalTask: null,
      priorityFilter: [0, 1, 2, 3, 4],
      priorityFilterOptions: [
        { text: "P0", value: 1 },
        { text: "P1", value: 1 },
        { text: "P2", value: 2 },
        { text: "P3", value: 3 },
        { text: "P4", value: 4 },
      ],
      searchFilter: "",
      statusFilter: ["open"],
      statusFilterOptions: [
        { text: "open", value: "open" },
        { text: "fixed", value: "fixed" },
        { text: "won't fix", value: "wontfix" },
        { text: "obsolete", value: "obsolete" },
        { text: "duplicate", value: "duplicate" },
      ],
      tasks: [],
    };
  },

  computed: {
    filteredTasks() {
      const searchFilterLowerCase = this.searchFilter.toLowerCase();
      return this.tasks.filter((task) => {
        if (this.statusFilter.indexOf(task.status) === -1) {
          return false;
        }

        let satisfiedDeadlineFilter = false;
        for (const deadline of this.deadlineFilter) {
          if (deadline === null) {
            if (task.deadline === null) {
              satisfiedDeadlineFilter = true;
            }
          } else if (deadline === "any") {
            satisfiedDeadlineFilter = true;
          } else {
            if (task.deadline !== null && task.deadline <= deadline) {
              satisfiedDeadlineFilter = true;
            }
          }

          if (satisfiedDeadlineFilter) {
            break;
          }
        }

        if (!satisfiedDeadlineFilter) {
          return false;
        }

        if (
          searchFilterLowerCase.length >= 3 &&
          !task.title.toLowerCase().includes(searchFilterLowerCase)
        ) {
          return false;
        }

        return true;
      });
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
    refreshTask(id) {
      // TODO(2021-09-28): `taskService.updateTask` should return a fully-
      // constructed task (and not just the database row, which lacks properties
      // like comments and updates) so we don't need to refresh here.
      this.loading = true;
      taskService.getTask(id).then((task) => {
        this.loading = false;
        for (let i = 0; i < this.tasks.length; i++) {
          if (this.tasks[i].id === task.id) {
            this.tasks.splice(i, 1, task);
            break;
          }
        }
      });
    },

    todayPlusN(nDays) {
      return this.todayAdjusted().plus({ days: nDays }).toISODate();
    },
  },
};
</script>

<style scoped>
table {
  font-size: 0.9rem;
}

.bi-pencil-fill {
  cursor: pointer;
}

h1,
.controls,
.search {
  margin-bottom: 20px;
}

.controls {
  display: flex;
  flex-direction: row;
  gap: 30px;
  font-size: 0.8rem;
}

.controls fieldset {
  margin-bottom: 0;
}

.search input {
  max-width: 400px;
}

h1 {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.add-task-button {
  cursor: pointer;
  margin-left: auto;
}
</style>
