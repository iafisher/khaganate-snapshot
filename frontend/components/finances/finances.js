import { DateTime } from "luxon";

export const EARLIEST_MONTH_OF_DATA = DateTime.fromObject({
  year: 2022,
  month: 2,
});

export function getSelect2Options(url) {
  return {
    ajax: { url, dataType: "json" },
    createTag: function (params) {
      // Attach a `newTag` property for `templateResult`.
      return {
        id: params.term,
        text: params.term,
        newTag: true,
      };
    },
    insertTag: function (data, tag) {
      // Place "Create '___'" options at the end of the list.
      data.push(tag);
    },
    // Allow dynamic creation of new options.
    tags: true,
    templateResult: function (tag) {
      // Display text as "Create '___'" for new tags by checking the `newTag`
      // property that would have been attached in `createTag`.
      return tag.newTag ? `Create '${tag.text}'` : tag.text;
    },
    width: "100%",
  };
}
