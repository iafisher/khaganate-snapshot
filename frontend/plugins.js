import * as apiService from "services/api_service.js";
import * as popupService from "services/popup_service.js";

export const ApiPlugin = {
  install(Vue) {
    Vue.prototype.$apiGet = apiService.get;
    Vue.prototype.$apiPost = apiService.post;
  },
};

export const DatabasePlugin = {
  install(Vue) {
    Vue.prototype.$dbQuery = function (sql) {
      return apiService.post("/api/db/sql", { sql: sql });
    };
  },
};

export const PopupPlugin = {
  install(Vue) {
    Vue.prototype.$popup = popupService.popup;
  },
};
