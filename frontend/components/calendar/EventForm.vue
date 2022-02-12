<template>
  <div>
    <div v-if="saving" class="text-center">
      <b-spinner />
    </div>

    <b-form @submit.prevent="onSubmit">
      <template v-if="!event || !event.recurring">
        <b-form-group label="Date" label-for="input-date">
          <b-form-input
            id="input-date"
            v-model="form.date"
            type="date"
            required
          />
        </b-form-group>

        <b-form-group label="Title" label-for="input-title">
          <b-form-input id="input-title" v-model="form.title" required />
        </b-form-group>

        <b-form-group label="Description" label-for="input-description">
          <b-textarea id="input-description" v-model="form.description" />
        </b-form-group>

        <b-form-group
          label="Location"
          label-for="input-location"
          description="Enter in the form '<street address> (<name>)'."
        >
          <b-form-input id="input-location" v-model="form.location" />
        </b-form-group>

        <b-form-group label="Start" label-for="input-start">
          <b-form-input
            id="input-start"
            v-model="form.start"
            type="time"
            required
          />
        </b-form-group>

        <b-form-group label="End" label-for="input-end">
          <b-form-input
            id="input-end"
            v-model="form.end"
            type="time"
            required
          />
        </b-form-group>

        <b-form-group
          label="Travel time (minutes)"
          label-for="input-travel-time"
        >
          <b-form-input
            id="input-travel-time"
            v-model="form.travelTime"
            type="number"
            min="0"
            :number="true"
          />
        </b-form-group>

        <b-form-group label="Duration" label-for="input-duration">
          <b-form-input id="input-duration" v-model="eventDuration" disabled />
        </b-form-group>

        <b-form-group>
          <b-checkbox v-model="form.maybe">Maybe</b-checkbox>
        </b-form-group>
      </template>

      <div class="text-center">
        <b-button
          v-if="!event || !event.recurring"
          type="submit"
          variant="primary"
        >
          Submit
        </b-button>
        <b-button v-if="event" variant="danger" @click="onDelete">
          Delete
        </b-button>
      </div>
    </b-form>
  </div>
</template>

<script>
import * as lodash from "lodash";

import { convertTimeStringToMinutes, pluralize } from "common.js";

export default {
  props: {
    event: { type: Object, required: false, default: null },
  },
  emits: ["event-deleted", "form-submitted"],

  data() {
    let form;
    if (this.event === null) {
      form = {
        date: null,
        title: "",
        description: "",
        location: "",
        maybe: false,
        start: null,
        end: null,
        travelTime: null,
      };
    } else {
      form = {
        date: this.event.startDate,
        title: this.event.title,
        description: this.event.description,
        location: this.event.location,
        maybe: this.event.maybe,
        start: this.event.start,
        end: this.event.end,
        travelTime: this.event.travelTime,
      };
    }

    return {
      form,
      saving: false,
    };
  },

  computed: {
    eventDuration() {
      if (
        this.form.start === null ||
        this.form.start === "" ||
        this.form.end === null ||
        this.form.end === ""
      ) {
        return null;
      }

      const startSplit = this.form.start.split(":");
      const startMinutes =
        parseInt(startSplit[0]) * 60 + parseInt(startSplit[1]);

      const endSplit = this.form.end.split(":");
      const endMinutes = parseInt(endSplit[0]) * 60 + parseInt(endSplit[1]);

      if (endMinutes <= startMinutes) {
        return "invalid duration";
      }

      const diffMinutes = endMinutes - startMinutes;
      const hours = Math.floor(diffMinutes / 60);
      const minutes = diffMinutes % 60;

      if (hours === 0) {
        return pluralize(minutes, "minute");
      } else {
        if (minutes === 0) {
          return pluralize(hours, "hour");
        } else {
          return `${pluralize(hours, "hour")}, ${pluralize(minutes, "minute")}`;
        }
      }
    },

    formForSubmission() {
      const form = lodash.cloneDeep(this.form);
      form.startDate = form.date;
      form.endDate = form.date;
      delete form.date;
      return form;
    },
  },

  methods: {
    onDelete() {
      this.saving = true;
      if (this.event.recurring) {
        const payload = {
          recurringEvent: this.event.id,
          date: this.event.startDate,
        };
        this.$apiPost(
          "/api/db/create/calendar-recurring-event-exceptions",
          payload
        ).then(() => {
          this.saving = false;
          this.$emit("event-deleted", this.event);
        });
      } else {
        this.$apiPost(`/api/db/delete/calendar-events/${this.event.id}`).then(
          () => {
            this.saving = false;
            this.$emit("event-deleted", this.event);
          }
        );
      }
    },

    onSubmit() {
      this.saving = true;
      if (this.event) {
        this.$apiPost(
          `/api/db/update/calendar-events/${this.event.id}`,
          this.formForSubmission
        ).then((event) => {
          this.saving = false;
          // TODO(2021-09-26): Clean this up.
          event.startMinutes = convertTimeStringToMinutes(event.start);
          event.endMinutes = convertTimeStringToMinutes(event.end);
          this.$emit("form-submitted", event);
        });
      } else {
        this.$apiPost(
          "/api/db/create/calendar-events",
          this.formForSubmission
        ).then((event) => {
          this.saving = false;
          this.$emit("form-submitted", event);
        });
      }
    },
  },
};
</script>
