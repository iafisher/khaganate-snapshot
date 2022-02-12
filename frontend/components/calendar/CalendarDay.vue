<template>
  <div>
    <div
      v-for="event in allDayEvents"
      :key="event.id"
      class="all-day-event"
      :title="event.title"
    >
      <span class="event-title">{{ event.title }}</span>
    </div>
    <div :style="{ height: allDayEventPadding + 'px' }"></div>

    <div class="calendar">
      <calendar-event
        v-for="pair in eventPairs"
        :key="pair.event.id"
        :event="pair.event"
        :overlapping="pair.overlapping"
        :style="{
          position: 'absolute',
          top: getEventPosition(pair.event) + 'px',
        }"
        @component-clicked="onComponentClicked(pair.event)"
        @event-updated="onEventUpdated(pair.event)"
      />
      <div
        v-if="currentTime && timeToPosition(currentTimeInMinutes) > 0"
        class="current-time"
        :style="{
          top: timeToPosition(currentTimeInMinutes) + 'px',
        }"
      ></div>
    </div>

    <b-modal ref="event-modal" size="lg" ok-only>
      <template v-if="modalEvent !== null">
        <h3><markdown-inline :text="modalEvent.title"></markdown-inline></h3>
        <br />
        {{ formatTime(modalEvent.start) }} &ndash;
        {{ formatTime(modalEvent.end) }}

        <template v-if="modalEvent.description !== ''">
          <br />
          <br />
          <markdown-block :text="modalEvent.description"></markdown-block>
        </template>

        <template v-if="modalEvent.location">
          <br />
          <br />
          Location:
          <a :href="getMapsUrl(modalEvent)" target="_blank">{{
            modalEvent.location
          }}</a>
        </template>
      </template>
    </b-modal>

    <b-modal
      ref="edit-event-modal"
      size="lg"
      title="Edit event"
      :ok-disabled="true"
    >
      <template v-if="modalEvent !== null" #default="{ ok }">
        <event-form
          :event="modalEvent"
          @form-submitted="
            ok();
            $emit('event-updated', $event);
          "
          @event-deleted="
            ok();
            $emit('event-deleted', $event);
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

import { convertTimeStringToMinutes, formatTime } from "common.js";
import { durationToHeight, getMapsUrl, timeToPosition } from "./calendar.js";

import CalendarEvent from "./CalendarEvent.vue";
import EventForm from "./EventForm.vue";

const ALL_DAY_EVENT_HEIGHT = 24;
const ALL_DAY_EVENT_BOTTOM_MARGIN = 10;

export default {
  components: {
    CalendarEvent,
    EventForm,
  },
  props: {
    currentTime: { type: Object, required: false, default: null },
    events: { type: Array, required: true },
    allDayEvents: { type: Array, required: false, default: () => [] },
    maxAllDayEvents: { type: Number, required: false, default: 0 },
  },
  emits: ["event-deleted", "event-updated"],

  data() {
    return {
      isModalOpen: false,
      modalEvent: null,
    };
  },

  computed: {
    currentTimeInMinutes() {
      return this.currentTime
        ? this.currentTime.hour * 60 + this.currentTime.minute
        : 0;
    },

    allDayEventPadding() {
      if (this.maxAllDayEvents === 0) {
        return 0;
      } else {
        return (
          (this.maxAllDayEvents - this.allDayEvents.length) *
            ALL_DAY_EVENT_HEIGHT +
          ALL_DAY_EVENT_BOTTOM_MARGIN
        );
      }
    },

    eventPairs() {
      const eventPairs = [];
      const eventQueue = [];

      // We iterate over the events array backwards because later events will
      // cover up earlier ones, so we need to mark the earlier ones as
      // overlapping so they can adjust their display accordingly.
      for (let i = this.events.length - 1; i >= 0; i--) {
        const event = this.events[i];
        while (
          eventQueue.length > 0 &&
          eventQueue[0].event.startMinutes >= event.endMinutes
        ) {
          eventQueue.shift();
        }

        let overlapping;
        if (eventQueue.length > 0) {
          if (eventQueue.length > 1) {
            throw "too many overlapping events";
          }

          const overlappingEvent = eventQueue[0].event;
          if (
            event.startMinutes <= overlappingEvent.startMinutes &&
            event.endMinutes >= overlappingEvent.endMinutes
          ) {
            // Mark the smaller event as overlapping.
            eventQueue[0].overlapping = true;
            overlapping = false;
          } else {
            overlapping = true;
          }
        } else {
          overlapping = false;
        }

        const pair = { event, overlapping };
        eventPairs.push(pair);
        eventQueue.push(pair);
      }

      eventPairs.reverse();
      return eventPairs;
    },
  },

  methods: {
    durationToHeight,
    getMapsUrl,
    timeToPosition,

    onComponentClicked(event) {
      this.modalEvent = event;
      this.$refs["event-modal"].show();
    },

    formatTime(timeOrString) {
      if (lodash.isString(timeOrString)) {
        return formatTime(convertTimeStringToMinutes(timeOrString));
      } else {
        return formatTime(timeOrString);
      }
    },

    getEventPosition(event) {
      return timeToPosition(event.startMinutes);
    },

    onEventUpdated(event) {
      this.modalEvent = event;
      this.$refs["edit-event-modal"].show();
    },
  },
};
</script>

<style scoped>
.calendar {
  position: relative; /* So that children can use absolute positioning. */
  background-color: whitesmoke;
  border: 1px solid darkgray;
  width: 175px;
  height: 600px;
}

.all-day-event {
  padding: 3px;
  font-size: 0.7rem;
  background: lightyellow;
  border: 1px solid darkgray;
  width: 165px;
  margin: auto;
  height: 24px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.current-time {
  position: absolute;
  height: 0;
  width: 100%;
  border: 1px solid red;
}
</style>
