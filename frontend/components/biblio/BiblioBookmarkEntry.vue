<template>
  <div>
    <!-- `secondary` is silver and `warning` is gold. -->
    <b-icon
      v-if="bookmark.quality > 1"
      icon="star-fill"
      :variant="bookmark.quality === 2 ? 'secondary' : 'warning'"
    ></b-icon>
    <span class="font-sm mr-1">#{{ bookmark.id }}:</span>
    <template v-if="bookmark.url !== ''">
      <a :href="bookmark.url">
        {{ bookmark.title }}
      </a>
    </template>
    <template v-else>
      {{ bookmark.title }}
    </template>
    <span class="font-sm ml-1">
      (saved <date-link :date="bookmark.createdAt" /><template
        v-if="bookmark.pdf !== ''"
        >;
        <a :href="'/api/files/raw/' + bookmark.pdf" target="_blank"
          >PDF available</a
        ></template
      >)
      <span class="ml-1 pointer">
        <b-icon v-if="!editing" icon="pencil-fill" @click="onEdit"></b-icon>
        <template v-else>
          <b-icon icon="file-earmark-check" @click="onFinish"></b-icon>
          <b-icon icon="x" @click="editing = false"></b-icon>
        </template>
      </span>
    </span>
    <markdown-block
      v-if="bookmark.annotation != '' && !editing"
      class="annotation"
      :text="bookmark.annotation"
    />
    <template v-if="editing">
      <b-overlay :show="saving">
        <b-textarea v-model="form.annotation"></b-textarea>
      </b-overlay>

      <b-overlay :show="loadingTopics || saving">
        <b-form-tags v-model="form.topics" tag-pills></b-form-tags>
      </b-overlay>
    </template>
  </div>
</template>

<script>
export default {
  props: {
    bookmark: { type: Object, required: true },
  },
  emits: ["bookmark-updated"],

  data() {
    return {
      editing: false,
      form: {
        annotation: this.bookmark.annotation,
        topics: [],
      },
      loadingTopics: false,
      saving: false,
    };
  },

  methods: {
    onEdit() {
      this.editing = true;
      this.loadingTopics = true;
      this.$apiGet(
        `/api/bookmarks/topics/get-for-bookmark/${this.bookmark.id}`
      ).then((topics) => {
        this.loadingTopics = false;
        this.form.topics = topics;
      });
    },

    onFinish() {
      this.editing = false;
      this.saving = true;
      this.$apiPost(
        `/api/bookmarks/update/${this.bookmark.id}`,
        this.form
      ).then((bookmark) => {
        this.saving = false;
        this.$emit("bookmark-updated", bookmark);
      });
    },
  },
};
</script>

<style scoped>
.annotation {
  margin: 0.75rem;
  margin-right: 0;
  font-size: 0.8rem;
}

.bi-star-fill {
  position: absolute;
  top: 4px;
  left: -22px;
}
</style>
