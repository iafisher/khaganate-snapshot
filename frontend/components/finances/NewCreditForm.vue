<template>
  <div>
    <b-alert v-model="saved" variant="success" class="text-center">
      <template v-if="lastSavedObject">
        Saved {{ lastSavedObject.amount | usd }} at
        {{
          lastSavedObject.vendor ? lastSavedObject.vendor.name : "(no vendor)"
        }}.
      </template>
      <template v-else>Saved!</template>
    </b-alert>

    <div v-if="saving" class="text-center">
      <b-spinner />
    </div>

    <b-form @submit.prevent="onSubmit">
      <b-form-group label="payment method" label-for="input-payment-method">
        <b-form-select v-model="form.paymentMethod" :required="true">
          <b-form-select-option value="Credit card"
            >Credit card</b-form-select-option
          >
          <b-form-select-option value="Debit card"
            >Debit card</b-form-select-option
          >
          <b-form-select-option value="Cash">Cash</b-form-select-option>
          <b-form-select-option value="Venmo">Venmo</b-form-select-option>
        </b-form-select>
      </b-form-group>

      <b-form-group label="amount" label-for="input-amount">
        <b-form-input
          id="input-amount"
          v-model="form.amount"
          type="number"
          step="0.01"
          min="0"
          required
          :number="true"
        />
      </b-form-group>

      <b-form-group label="date paid" label-for="input-date-paid">
        <b-form-input
          id="input-date-paid"
          v-model="form.datePaid"
          type="date"
          required
        />
      </b-form-group>

      <b-form-group label="date incurred" label-for="input-date-incurred">
        <b-form-input
          id="input-date-incurred"
          v-model="form.dateIncurred"
          type="date"
        />
      </b-form-group>

      <b-form-group label="vendor">
        <select2 v-model="form.vendor" :options="select2OptionsVendor" />
      </b-form-group>

      <b-form-group label="category">
        <select2
          v-model="form.category"
          :options="select2OptionsCategory"
          :required="true"
        />
      </b-form-group>

      <b-form-group label="notes" label-for="input-notes">
        <b-form-input id="input-notes" v-model="form.notes" type="text" />
      </b-form-group>

      <div class="text-center">
        <b-button type="submit" variant="primary">Submit</b-button>
        <b-button class="submit-and-another" type="submit" variant="secondary">
          Submit and add another
        </b-button>
      </div>
    </b-form>
  </div>
</template>

<script>
import { DateTime } from "luxon";

import { getSelect2Options } from "./finances.js";

export default {
  emits: ["form-submitted"],

  data() {
    return {
      form: {
        amount: null,
        category: null,
        datePaid: DateTime.local().toISODate(),
        dateIncurred: null,
        notes: "",
        paymentMethod: null,
        vendor: null,
      },
      lastSavedObject: null,
      saved: false,
      saving: false,
      select2OptionsCategory: getSelect2Options(
        "/api/finances/credit-categories/autocomplete"
      ),
      select2OptionsVendor: getSelect2Options(
        "/api/finances/vendors/autocomplete"
      ),
    };
  },

  methods: {
    onSubmit(event) {
      const andAddAnother = event.submitter.classList.contains(
        "submit-and-another"
      );
      this.saving = true;
      this.$apiPost("/api/finances/credits/create", this.form).then(
        (credit) => {
          this.lastSavedObject = credit;
          this.saving = false;
          this.saved = true;
          if (!andAddAnother) {
            this.$emit("form-submitted", credit);
          }
        }
      );
    },
  },
};
</script>
