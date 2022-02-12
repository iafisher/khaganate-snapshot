<template>
  <div class="task">
    <div class="task-bar">
      <span class="task-bar-left">
        <router-link
          v-if="!standalone"
          :to="{ name: 'task', params: { id: task.id } }"
          target="_blank"
        >
          <b-icon icon="link"></b-icon>
        </router-link>
        <markdown-inline class="title" :text="task.title" />
        <span
          v-if="!standalone && isOpen && task.deadline !== null"
          class="due-date"
        >
          due
          <span :class="{ 'due-soon': dueSoon }" :title="task.deadline">
            {{ dueDateString }}
          </span>
        </span>
      </span>

      <span class="task-bar-right">
        <b-icon
          class="edit-icon"
          icon="pencil-fill"
          @click.prevent="$bvModal.show(modalId)"
        ></b-icon>

        <span
          v-b-toggle="standalone ? null : 'collapse-task-' + task.id"
          :class="'comment-count ' + (standalone ? 'no-cursor' : '')"
        >
          <b-icon icon="chat-left"></b-icon>
          {{ task.comments.length }}
        </span>

        <b-button size="sm" variant="outline-success" @click="onMarkDone">
          Done
        </b-button>
      </span>
    </div>

    <b-collapse :id="'collapse-task-' + task.id" :visible="standalone">
      <markdown-block
        v-if="task.description !== ''"
        class="description"
        :text="task.description"
      />

      <table class="metadata">
        <tr>
          <td>Status:</td>
          <td>{{ task.status }}</td>
        </tr>
        <tr>
          <td>Priority:</td>
          <td>{{ task.priority }}</td>
        </tr>
        <tr v-if="standalone">
          <td>Deadline:</td>
          <td>
            <date-link
              v-if="task.deadline !== null && task.deadline !== ''"
              :date="task.deadline"
            />
            <template v-else>none</template>
          </td>
        </tr>
        <tr>
          <td>Created at:</td>
          <td><date-link :date="task.createdAt" :with-time="true" /></td>
        </tr>
        <tr>
          <td>Last updated at:</td>
          <td>
            <date-link :date="task.lastUpdatedAtOverall" :with-time="true" />
          </td>
        </tr>
      </table>

      <div class="history-checkboxes">
        <b-form-checkbox v-model="showUpdates"> Show updates </b-form-checkbox>

        <b-form-checkbox v-model="showTimeSlots">
          Show time slots
        </b-form-checkbox>
      </div>

      <div class="comments">
        <div
          v-for="comment in commentsAndUpdates"
          :key="comment.type + comment.data.id"
          :class="{
            comment: true,
            'machine-comment': comment.type !== 'comment',
          }"
        >
          <template v-if="comment.type === 'comment'">
            <date-link
              class="timestamp"
              :date="comment.data.createdAt"
              :with-time="true"
            />
            <markdown-block :text="comment.data.text" />
          </template>
          <template v-else-if="comment.type === 'update'">
            Field <code>{{ comment.data.field }}</code>
            <template
              v-if="
                comment.data.oldValue !== '' && comment.data.newValue !== ''
              "
            >
              changed from
              <code>{{ comment.data.oldValue }}</code>
              to
              <code>{{ comment.data.newValue }}</code>
            </template>
            <template v-else-if="comment.data.oldValue !== ''">
              set blank
            </template>
            <template v-else>
              set to <code>{{ comment.data.newValue }}</code>
            </template>
            at <date-link :date="comment.data.createdAt" :with-time="true" />.
          </template>
          <template v-else-if="comment.type === 'timeSlot'">
            Time slot of
            <strong>{{ comment.data.minutes | pluralize("minute") }}</strong> on
            <date-link :date="comment.data.date" />.
          </template>
          <template v-else>
            Error: unknown comment type: <code>{{ comment.type }}</code>
          </template>
        </div>

        <b-textarea v-model="newCommentForm.text"></b-textarea>
        <b-button variant="primary" @click="onCommentCreated">
          New comment
        </b-button>
      </div>
    </b-collapse>

    <b-modal :id="modalId" size="lg" :ok-disabled="true" title="Edit task">
      <template #default="{ ok }">
        <task-form
          :task="task"
          @form-submitted="
            ok();
            onTaskUpdated($event);
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
import { isOpen } from "./tasks.js";

export default {
  components: {
    TaskForm,
  },
  props: {
    task: { type: Object, required: true },
    standalone: { type: Boolean, required: false, default: false },
  },
  emits: [
    "comment-created",
    "task-updated",
    "task-deadline-updated",
    "time-slot-created",
  ],

  data() {
    return {
      newCommentForm: {
        text: "",
      },
      showTimeSlots: false,
      showUpdates: false,
    };
  },

  computed: {
    commentsAndUpdates() {
      const r = [];

      for (const comment of this.task.comments) {
        r.push({ type: "comment", data: comment });
      }

      if (this.showTimeSlots) {
        for (const timeSlot of this.task.timeSlots) {
          r.push({ type: "timeSlot", data: timeSlot });
        }
      }

      for (const update of this.task.updates) {
        if (this.showUpdates || update.field === "status") {
          r.push({ type: "update", data: update });
        }
      }

      return lodash.sortBy(r, [(o) => o.data.createdAt]);
    },

    dueDateString() {
      if (this.numberOfDaysDue > 1) {
        return `in ${this.numberOfDaysDue} days`;
      } else if (this.numberOfDaysDue === 1) {
        return "tomorrow";
      } else if (this.numberOfDaysDue === 0) {
        return "today";
      } else if (this.numberOfDaysDue === -1) {
        return "yesterday";
      } else {
        return `${-this.numberOfDaysDue} days ago`;
      }
    },

    dueSoon() {
      return this.numberOfDaysDue !== null && this.numberOfDaysDue <= 2;
    },

    isOpen() {
      return isOpen(this.task);
    },

    modalId() {
      return "edit-task-modal-" + this.task.id;
    },

    numberOfDaysDue() {
      if (this.task.deadline === null) {
        return null;
      }

      const now = this.todayAdjusted().startOf("day");
      const then = DateTime.fromISO(this.task.deadline).startOf("day");

      return Math.floor(then.diff(now, "days").days);
    },
  },

  methods: {
    onTaskUpdated(task) {
      this.$emit("task-updated", task);
    },

    onCommentCreated() {
      taskService
        .createComment(this.task.id, this.newCommentForm)
        .then((newComment) => {
          this.newCommentForm.text = "";
          this.$popup(
            `Created comment on task '${this.task.title}' (${this.task.id}).`,
            { autoDismiss: true }
          );
          this.$emit("comment-created", newComment);
        });
    },

    onMarkDone() {
      taskService.markFixed(this.task.id).then((newTask) => {
        this.$emit("task-updated", newTask);
      });
    },
  },
};
</script>

<style scoped>
.task {
  border: 1px solid #ccc;
  padding: 10px;
}

.task-bar {
  display: flex;
  flex-direction: row;
}

.task-bar .title {
  margin-left: 5px;
  font-size: 1.2rem;
}

.task-bar .due-date {
  margin-left: 10px;
  font-size: 0.8rem;
  opacity: 75%;
  align-self: center;
  white-space: nowrap;
}

.task-bar .task-bar-left {
  flex-grow: 0;
}

.task-bar .task-bar-right {
  margin-left: auto;
  flex-shrink: 0;
}

.task-bar .edit-icon {
  cursor: pointer;
  margin-right: 7px;
}

.task + .task {
  border-top-width: 0px;
}

.task .description,
.task .metadata,
.task .history-checkboxes,
.task .comments {
  margin-top: 15px;
}

.task .metadata {
  font-size: 0.8rem;
}

.task .metadata td:first-child {
  font-weight: bold;
  padding-right: 10px;
}

.task .history-checkboxes {
  display: flex;
  flex-direction: row;
  gap: 20px;
  font-size: 0.8rem;
}

.task .comment {
  border-radius: 5px;
  background-color: whitesmoke;
  border: 1px solid #ccc;
  padding: 10px;
}

.task .comment + .comment,
.task .comment + textarea,
.task textarea + button {
  margin-top: 10px;
}

.task .comment .timestamp {
  display: block;
  font-size: 0.8rem;
  border-bottom: 1px solid #ccc;
  margin-bottom: 10px;
}

.task .machine-comment {
  font-size: 0.8rem;
}

.task .time-slot-form {
  display: inline;
}

.task .time-slot-input {
  display: inline;
  width: 70px;
}

.no-cursor {
  cursor: default;
}

.due-soon {
  color: red;
}
</style>
