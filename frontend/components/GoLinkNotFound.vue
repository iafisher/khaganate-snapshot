<template>
  <div class="page">
    <h2 class="text-center">Link not found</h2>
    <p v-if="!created">Sorry, go/{{ path }} does not exist.</p>
    <p>
      Create it?
      <input v-model="target" type="text" :disabled="created" />
      <b-button variant="primary" :disabled="created" @click="onSubmit">
        Submit
      </b-button>
    </p>
    <p v-if="created">
      <a :href="'http://go/' + path">go/{{ path }}</a> created!
    </p>
  </div>
</template>

<script>
export default {
  props: {
    path: { type: String, required: true },
  },

  data() {
    return {
      created: false,
      target: "",
    };
  },

  methods: {
    onSubmit() {
      this.$apiPost("/api/db/create/golinks", {
        linkText: this.path,
        path: this.target,
      }).then(() => {
        this.created = true;
      });
    },
  },
};
</script>
