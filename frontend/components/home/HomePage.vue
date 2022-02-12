<template>
  <div class="page-full">
    <h1 class="page-header">
      <date-link :date="today()" />
    </h1>

    <b-row>
      <b-col class="mr-2 w-50">
        <b-row class="mb-2">
          <b-card>
            <habits-card @habit-created="refreshGoals += 1" />
          </b-card>
        </b-row>

        <b-row class="mb-2">
          <b-card class="calendar-card mb-2 mr-2">
            <h2>
              <router-link :to="{ name: 'calendar-today' }" target="_blank">
                Calendar
              </router-link>
            </h2>

            <calendar-range
              :start="calendarStart"
              :end="calendarEnd"
              :refresh="refreshCalendar"
            />
          </b-card>

          <b-card title="Quick links" class="quick-links-card mb-2">
            <b-card-body>
              <b-list-group>
                <b-list-group-item v-b-modal="'new-credit-modal'">
                  New credit
                </b-list-group-item>
                <b-list-group-item v-b-modal="'new-event-modal'">
                  New event
                </b-list-group-item>
              </b-list-group>
            </b-card-body>
          </b-card>
        </b-row>

        <b-row>
          <b-card title="Recent bookmarks" class="bookmarks-card">
            <b-card-body>
              <ul>
                <li v-for="bookmark in recentBookmarks" :key="bookmark.id">
                  <a :href="bookmark.url">{{ bookmark.title }}</a>
                </li>
              </ul>
            </b-card-body>
          </b-card>
        </b-row>
      </b-col>
      <b-col class="w-50">
        <b-row class="mb-2">
          <b-card class="task-card">
            <task-inbox @task-updated="refreshGoals += 1" />
          </b-card>
        </b-row>
        <b-row>
          <b-card>
            <goals-card
              :year="today().year"
              :month="today().month"
              :refresh="refreshGoals"
            />
          </b-card>
        </b-row>
      </b-col>
    </b-row>

    <b-modal
      id="new-credit-modal"
      size="lg"
      :ok-disabled="true"
      title="New credit"
    >
      <template #default="{ ok }">
        <new-credit-form
          @form-submitted="
            ok();
            refreshGoals += 1;
          "
        />
      </template>

      <template #modal-footer>
        <span></span>
      </template>
    </b-modal>

    <b-modal
      id="new-event-modal"
      size="lg"
      :ok-disabled="true"
      title="New event"
    >
      <template #default="{ ok }">
        <event-form
          @form-submitted="
            ok();
            refreshCalendar += 1;
          "
          @event-deleted="
            ok();
            refreshCalendar += 1;
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
import CalendarRange from "components/calendar/CalendarRange.vue";
import EventForm from "components/calendar/EventForm.vue";
import GoalsCard from "components/goals/GoalsCard.vue";
import HabitsCard from "components/habits/HabitsCard.vue";
import NewCreditForm from "components/finances/NewCreditForm.vue";
import TaskInbox from "components/tasks/TaskInbox.vue";

export default {
  components: {
    CalendarRange,
    EventForm,
    GoalsCard,
    HabitsCard,
    NewCreditForm,
    TaskInbox,
  },

  data() {
    return {
      logFileAlerts: [],
      needsBreakfastForm: false,
      needsLunchForm: false,
      needsDinnerForm: false,
      needsPulseCheckForm: false,
      needsSleepForm: false,
      refreshCalendar: 0,
      refreshGoals: 0,
      updatingHeadlines: false,
      recentBookmarks: [],
    };
  },

  computed: {
    calendarStart() {
      return this.today();
    },

    calendarEnd() {
      return this.today().plus({ days: 3 });
    },

    alerts() {
      const alerts = [];
      for (const logFileAlert of this.logFileAlerts) {
        alerts.push({
          message: `Log file alert: ${logFileAlert}`,
          level: "severe",
        });
      }
      return alerts;
    },
  },

  created() {
    this.$apiGet(
      "/api/db/list/bookmarks?__limit=7&__order_by=created_at&__order_desc"
    ).then((bookmarks) => {
      this.recentBookmarks = bookmarks;
    });
  },
};
</script>

<style scoped>
.page-header {
  font-size: 1.5rem;
  margin-bottom: 20px;
}

.calendar-box {
  display: flex;
  flex-direction: row;
}

.calendar-box h3 {
  font-size: 1rem;
  text-align: center;
}

.overdue {
  color: red;
}

.time-slot-form select {
  max-width: 300px;
}

.time-slot-form input[type="number"] {
  max-width: 70px;
}

.task-card {
  flex-grow: 1;
}

.bookmarks-card,
.quick-links-card {
  flex-grow: 1;
}

.quick-links-card {
  margin-top: 0;
}

.calendar-card h2 {
  margin-bottom: 16px;
}

.calendar-card h2 a {
  color: initial;
  text-decoration: underline;
}
</style>
