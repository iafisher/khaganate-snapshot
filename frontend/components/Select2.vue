<template>
  <select :disabled="disabled" :required="required"></select>
</template>

<script>
// https://codesandbox.io/s/github/vuejs/vuejs.org/tree/master/src/v2/examples/vue-20-wrapper-component?from-embed
// https://github.com/ncasich/vue-select-search/blob/master/SelectSearch.vue
import $ from "jquery";
import Select2 from "select2/dist/js/select2.js";
import "select2/dist/css/select2.min.css";

// Need to call Select2 explicitly for it to register itself with jQuery.
// https://coderedirect.com/questions/479356/nodejs-with-webpack-jquery-deferred-exception-o-select2-is-not-a-function
Select2();

export default {
  props: {
    disabled: { type: Boolean, required: false, default: false },
    required: { type: Boolean, required: false, default: false },
    options: { type: Object, required: true },
    // Updates to this property after initialization will be ignored.
    value: { type: Object, required: false, default: null },
  },
  emits: ["input"],

  watch: {
    options() {
      $(this.$el).empty().select2(this.options);
    },
  },

  mounted() {
    // Ensure Select2 works correctly inside of Bootstrap modals.
    //
    // https://select2.org/troubleshooting/common-problems#select2-does-not-function-properly-when-i-use-it-inside-a-bootst
    const e = $(this.$el).parents(".modal-content");
    if (e.length > 0) {
      // eslint-disable-next-line vue/no-mutating-props
      this.options.dropdownParent = e[0];
    }

    const vm = this;
    $(this.$el)
      .select2(this.options)
      .val(this.value)
      .trigger("change")
      .on("select2:select", (e) => {
        vm.$emit("input", e.params.data);
      });
  },

  destroyed() {
    $(this.$el).off().select2("destroy");
  },
};
</script>
