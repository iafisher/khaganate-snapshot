<template>
  <div
    :class="['event-container', { overlapping }]"
    @click="$emit('component-clicked')"
  >
    <div
      class="travel-time top"
      :style="{
        top: -travelTimeHeight + 'px',
        height: travelTimeHeight + 'px',
      }"
    ></div>
    <div
      :class="[
        'event',
        {
          maybe: event.maybe,
          recurring: event.recurring,
        },
      ]"
      :style="{ height }"
    >
      <div class="title-row">
        <span class="title">
          <!-- TODO(2021-08-03): Is there a more concise way to write this? -->
          <a v-if="event.location" :href="mapsUrl" target="_blank">
            <abbr
              v-if="event.description !== ''"
              title="Click to see event description"
            >
              {{ event.title }}
            </abbr>
            <template v-else>
              {{ event.title }}
            </template>
          </a>
          <template v-else>
            <abbr
              v-if="event.description !== ''"
              title="Click to see event description"
            >
              {{ event.title }}
            </abbr>
            <template v-else>
              {{ event.title }}
            </template>
          </template>
        </span>
        <b-icon
          v-if="!event.recurring"
          class="pointer"
          icon="pencil-fill"
          @click.stop="$emit('event-updated')"
        ></b-icon>
        <b-icon
          v-else
          class="pointer"
          icon="trash"
          @click.stop="$emit('event-updated')"
        ></b-icon>
      </div>
      <div class="timespan-row">
        <span class="timespan">
          {{ formatTime(event.startMinutes) }} &ndash;
          {{ formatTime(event.endMinutes) }}
        </span>
      </div>
    </div>
    <div
      class="travel-time bottom"
      :style="{ height: travelTimeHeight + 'px' }"
    ></div>
  </div>
</template>

<script>
import { formatTime } from "common.js";
import { EVENT_HEIGHT, durationToHeight, getMapsUrl } from "./calendar.js";

export default {
  props: {
    event: { type: Object, required: true },
    overlapping: { type: Boolean, required: false, default: false },
  },
  emits: ["component-clicked", "event-updated"],

  computed: {
    height() {
      return (
        Math.max(
          durationToHeight(this.event.endMinutes - this.event.startMinutes),
          EVENT_HEIGHT
        ) + "px"
      );
    },

    travelTimeHeight() {
      return durationToHeight(this.event.travelTime);
    },

    mapsUrl() {
      return getMapsUrl(this.event);
    },
  },

  methods: {
    formatTime,
  },
};
</script>

<style scoped>
.event-container {
  width: 100%;
  /* So that the .travel-time child can be absolutely positioned. */
  position: relative;
  cursor: pointer;
}

.event-container.overlapping {
  width: 50%;
  margin-left: 50%;
  z-index: 1000;
}

.event {
  padding: 3px;
  font-size: 0.7rem;
  background: lightyellow;
  border-top: 1px solid darkgray;
  border-bottom: 1px solid darkgray;
  width: 100%;
}

.overlapping .event {
  border-left: 1px solid darkgray;
}

.event.maybe {
  background: repeating-linear-gradient(
    -45deg,
    lightgray,
    lightgray 20px,
    lightyellow 20px,
    lightyellow 40px
  );
}

.event.recurring {
  background: azure;
}

.title-row,
.timespan-row {
  display: flex;
  flex-direction: row;
}

.title {
  width: 155px;
}

.title,
.timespan {
  /* Guarantee that it will appear on one line. */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.title-row .b-icon {
  margin-left: auto;
}

.travel-time {
  background: lightyellow;
  opacity: 40%;
  width: 100%;
}

.travel-time.top {
  position: absolute;
  border-top: 1px solid darkgray;
}

.travel-time.bottom {
  border-bottom: 1px solid darkgray;
}

.overlapping .travel-time {
  border-left: 1px solid darkgray;
}
</style>
