<template>
  <b-modal :id="id" size="lg" :ok-disabled="true">
    <template #modal-title>
      <slot name="title">{{ title }}</slot>
    </template>

    <template #default="{ ok }">
      <b-form
        @submit.prevent="
          ok();
          onSubmit();
        "
      >
        <div v-if="submitting" class="text-center">
          <b-spinner />
        </div>

        <b-form-group
          v-for="(field, i) in fields"
          :key="field.key"
          :label="field.type !== 'checkbox' ? field.label : ''"
          :label-for="field.type !== 'checkbox' ? 'input-' + field.key : ''"
          :description="field.description"
        >
          <b-checkbox v-if="field.type === 'checkbox'" v-model="inputs[i]">
            {{ field.label }}
          </b-checkbox>
          <b-form-input
            v-else
            :id="'input-' + field.key"
            v-model="inputs[i]"
            :type="field.type"
            :number="field.type === 'number'"
            :max="field.max"
            :min="field.min"
            :step="field.step"
            :required="field.required"
          />
        </b-form-group>

        <div class="text-center">
          <b-button type="submit" variant="primary">Submit</b-button>
        </div>
      </b-form>
    </template>

    <template #modal-footer>
      <span></span>
    </template>
  </b-modal>
</template>

<script>
export default {
  props: {
    id: { type: String, required: true },
    title: { type: String, required: false, default: "" },
    url: { type: String, required: true },
    fields: { type: Array, required: true },
    data: { type: Object, required: false, default: null },
  },
  emits: ["form-submitted"],

  data() {
    const inputs = [];
    for (let i = 0; i < this.fields.length; i++) {
      inputs.push(null);
    }
    this.setInputValues(inputs);

    return {
      inputs: inputs,
      submitting: false,
    };
  },

  computed: {
    form() {
      const form = {};
      for (let i = 0; i < this.fields.length; i++) {
        const field = this.fields[i];
        const input = this.inputs[i];
        form[field.key] = input;
      }
      return form;
    },
  },

  watch: {
    data() {
      this.setInputValues(this.inputs);
    },
  },

  methods: {
    onSubmit() {
      this.submitting = true;
      this.$apiPost(this.url, this.form).then((response) => {
        this.submitting = false;
        this.$emit("form-submitted", response);
      });
    },

    setInputValues(inputs) {
      for (let i = 0; i < this.fields.length; i++) {
        const field = this.fields[i];
        if (this.data !== null && !!this.data[field.key]) {
          inputs[i] = this.data[field.key];
        } else if (field.initial !== undefined) {
          inputs[i] = field.initial;
        } else {
          if (field.type === "text") {
            inputs[i] = "";
          } else if (field.type === "checkbox") {
            inputs[i] = false;
          } else {
            inputs[i] = null;
          }
        }
      }
    },
  },
};
</script>
