import { BootstrapVue, BootstrapVueIcons, IconsPlugin } from "bootstrap-vue";
import Vue from "vue";
import VueRouter from "vue-router";
import { isString } from "lodash";
import { DateTime } from "luxon";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-vue/dist/bootstrap-vue.css";

import AppComponent from "components/App.vue";
import BiblioHomePage from "components/biblio/BiblioHomePage.vue";
import BiblioTopicPage from "components/biblio/BiblioTopicPage.vue";
import BooksPage from "components/books/BooksPage.vue";
import BooksToReadPage from "components/books/BooksToReadPage.vue";
import CalendarPage from "components/calendar/CalendarPage.vue";
import DateLink from "components/DateLink.vue";
import EditPage from "components/explorer/EditPage.vue";
import FilePage from "components/explorer/FilePage.vue";
import FilmsPage from "components/films/FilmsPage.vue";
import FilmsToWatchPage from "components/films/FilmsToWatchPage.vue";
import FinancesCategoryPage from "components/finances/CategoryPage.vue";
import FinancesMonthPage from "components/finances/FinancesMonthPage.vue";
import FinancesReconciliationPage from "components/finances/FinancesReconciliationPage.vue";
import FinancesVendorPage from "components/finances/VendorPage.vue";
import FinancesYearPage from "components/finances/FinancesYearPage.vue";
import GitReviewPage from "components/git/GitReviewPage.vue";
import GoalsPage from "components/goals/GoalsPage.vue";
import GoLinkNotFound from "components/GoLinkNotFound.vue";
import HomePage from "components/home/HomePage.vue";
import JournalDayPage from "components/journal/DayPage.vue";
import JournalHomePage from "components/journal/HomePage.vue";
import JournalMonthPage from "components/journal/MonthPage.vue";
import LoadingBox from "components/LoadingBox.vue";
import MarkdownBlock from "components/MarkdownBlock.vue";
import MarkdownInline from "components/MarkdownInline.vue";
import MetricPage from "components/metrics/MetricPage.vue";
import MetricsMonthPage from "components/metrics/MetricsMonthPage.vue";
import ModalForm from "components/ModalForm.vue";
import MonthNav from "components/MonthNav.vue";
import NotFoundPage from "components/NotFoundPage.vue";
import QuizPage from "components/drill/QuizPage.vue";
import SearchResultsPage from "components/search/SearchResultsPage.vue";
import Select2 from "components/Select2.vue";
import TaskListPage from "components/tasks/TaskListPage.vue";
import TaskDetailPage from "components/tasks/TaskDetailPage.vue";
import TravelMapPage from "components/travel/TravelMapPage.vue";
import {
  formatDate,
  formatDollarAmount,
  formatIntegerWithCommas,
  getMonthName,
  pluralize,
} from "common.js";
import * as plugins from "./plugins.js";
import * as popupService from "./services/popup_service.js";

const routes = [
  {
    path: "",
    name: "home",
    component: HomePage,
  },
  {
    path: "/biblio",
    name: "biblio-home",
    component: BiblioHomePage,
    meta: { title: "Biblio | Khaganate" },
  },
  {
    path: "/biblio/:topic(.+)",
    name: "biblio-topic",
    component: BiblioTopicPage,
    props: true,
    meta: { title: "Biblio | Khaganate" },
  },
  {
    path: "/books",
    name: "books",
    component: BooksPage,
    props: { year: null, month: null },
    meta: { title: "Books | Khaganate" },
  },
  {
    path: "/books/:year(\\d+)",
    name: "books-year",
    component: BooksPage,
    props: (route) => ({ year: parseInt(route.params.year), month: null }),
    meta: { title: (route) => `Books, ${route.params.year} | Khaganate` },
  },
  {
    path: "/reading/:year(\\d+)/:month(\\d+)",
    name: "books-month",
    component: BooksPage,
    props: (route) => ({
      year: parseInt(route.params.year),
      month: parseInt(route.params.month),
    }),
    meta: {
      title: (route) =>
        `Books, ${getMonthName(parseInt(route.params.month))} ${
          route.params.year
        } | Khaganate`,
    },
  },
  {
    path: "/books/to-read",
    name: "books-to-read",
    component: BooksToReadPage,
    meta: { title: "Books to read | Khaganate" },
  },
  {
    path: "/calendar",
    name: "calendar-today",
    redirect: () => {
      const today = DateTime.local();
      return `/calendar/${today.year}/${today.month}/${today.day}`;
    },
  },
  {
    path: "/calendar/:year(\\d+)/:month(\\d+)/:day(\\d+)",
    name: "calendar",
    component: CalendarPage,
    props: (route) => ({
      year: parseInt(route.params.year),
      month: parseInt(route.params.month),
      day: parseInt(route.params.day),
    }),
    meta: {
      title: (route) =>
        `Calendar, ${getMonthName(parseInt(route.params.month))} ${
          route.params.day
        }, ${route.params.year} | Khaganate`,
    },
  },
  {
    path: "/drill",
    name: "drill",
    component: QuizPage,
    meta: { title: "Drill" },
  },
  {
    path: "/edit/files/:path*",
    name: "edit-file",
    component: EditPage,
    props: true,
    meta: {
      title: (route) =>
        `files/${
          isString(route.params.path)
            ? route.params.path
            : route.params.path.join("/")
        } (editing)`,
    },
  },
  {
    path: "/files",
    name: "file-home",
    component: FilePage,
    props: { path: "", revision: "" },
    meta: { title: "files/" },
  },
  {
    path: "/files/:path*",
    name: "file",
    component: FilePage,
    props: (route) => ({
      path: route.params.path,
      revision: route.query.r,
    }),
    meta: {
      title: (route) =>
        `files/${
          isString(route.params.path)
            ? route.params.path
            : route.params.path.join("/")
        }`,
    },
  },
  {
    path: "/films/to-watch",
    name: "films-to-watch",
    component: FilmsToWatchPage,
    meta: { title: "Films to watch | Khaganate" },
  },
  {
    path: "/films/:year(\\d+)?",
    name: "films",
    component: FilmsPage,
    props: (route) => ({
      year:
        route.params.year === undefined ? null : parseInt(route.params.year),
    }),
    meta: {
      title: (route) =>
        route.params.year === undefined
          ? "Films | Khaganate"
          : `Films ${route.params.year} | Khaganate`,
    },
  },
  {
    path: "/go/:path(.+)",
    name: "go-link-not-found",
    component: GoLinkNotFound,
    props: true,
    meta: { title: "Go Link Not Found | Khaganate" },
  },
  {
    path: "/goals/:year(\\d+)/:month(\\d+)",
    name: "goals-month",
    component: GoalsPage,
    props: (route) => ({
      year: parseInt(route.params.year),
      month: parseInt(route.params.month),
    }),
    meta: {
      title: (route) =>
        `Goals, ${getMonthName(parseInt(route.params.month))} ${
          route.params.year
        } | Khaganate`,
    },
  },
  {
    path: "/journal",
    name: "journal-home",
    component: JournalHomePage,
    meta: { title: "Journal | Khaganate" },
  },
  {
    path: "/journal/:year(\\d+)/:month(\\d+)",
    name: "journal-month",
    component: JournalMonthPage,
    props: (route) => ({
      year: parseInt(route.params.year),
      month: parseInt(route.params.month),
    }),
    meta: {
      title: (route) =>
        `Journal, ${getMonthName(parseInt(route.params.month))} ${
          route.params.year
        } | Khaganate`,
    },
  },
  {
    path: "/journal/:year(\\d+)/:month(\\d+)/:day(\\d+)",
    name: "journal-day",
    component: JournalDayPage,
    props: (route) => ({
      year: parseInt(route.params.year),
      month: parseInt(route.params.month),
      day: parseInt(route.params.day),
    }),
    meta: {
      title: (route) =>
        `Journal, ${getMonthName(parseInt(route.params.month))} ${
          route.params.day
        }, ${route.params.year} | Khaganate`,
    },
  },
  {
    path: "/finances",
    redirect: () => {
      const today = DateTime.local();
      return `/finances/${today.year}/${today.month}`;
    },
  },
  {
    path: "/finances/:year(\\d+)",
    name: "finances-year",
    component: FinancesYearPage,
    props: (route) => ({ year: parseInt(route.params.year) }),
    meta: { title: (route) => `Finances, ${route.params.year} | Khaganate` },
  },
  {
    path: "/finances/:year(\\d+)/:month(\\d+)",
    name: "finances-month",
    component: FinancesMonthPage,
    props: (route) => ({
      year: parseInt(route.params.year),
      month: parseInt(route.params.month),
    }),
    meta: {
      title: (route) =>
        `Finances, ${getMonthName(parseInt(route.params.month))} ${
          route.params.year
        } | Khaganate`,
    },
  },
  {
    path: "/finances/:year(\\d+)/:month(\\d+)/reconcile",
    name: "finances-month-reconciliation",
    component: FinancesReconciliationPage,
    props: (route) => ({
      year: parseInt(route.params.year),
      month: parseInt(route.params.month),
    }),
    meta: {
      title: (route) =>
        `Reconciliation for ${getMonthName(parseInt(route.params.month))} ${
          route.params.year
        } | Khaganate`,
    },
  },
  {
    path: "/finances/category/:category",
    name: "finances-category",
    component: FinancesCategoryPage,
    props: true,
    meta: { title: "Finances | Khaganate" },
  },
  {
    path: "/finances/category/:category/:subcategory",
    name: "finances-subcategory",
    component: FinancesCategoryPage,
    props: true,
    meta: { title: "Finances | Khaganate" },
  },
  {
    path: "/finances/vendor/:vendor(\\d+)",
    name: "finances-vendor",
    component: FinancesVendorPage,
    props: (route) => ({
      vendor: parseInt(route.params.vendor),
    }),
    meta: { title: "Vendor | Khaganate" },
  },
  {
    path: "/metrics",
    name: "metrics-redirect",
    redirect: () => {
      const today = DateTime.local();
      return `/metrics/${today.year}/${today.month}`;
    },
  },
  {
    path: "/metrics/:metricName",
    name: "metrics",
    component: MetricPage,
    props: true,
    meta: {
      title: (route) => `Metric: ${route.params.metricName} | Khaganate`,
    },
  },
  {
    path: "/metrics/:year(\\d+)/:month(\\d+)",
    name: "metrics-month",
    component: MetricsMonthPage,
    props: (route) => ({
      year: parseInt(route.params.year),
      month: parseInt(route.params.month),
    }),
    meta: {
      title: (route) =>
        `Metrics for ${getMonthName(parseInt(route.params.month))} ${
          route.params.year
        } | Khaganate`,
    },
  },
  {
    path: "/review/:path*",
    component: GitReviewPage,
    props: true,
    meta: { title: "Review | Khaganate" },
  },
  {
    path: "/search/:query(.+)",
    name: "search-results",
    component: SearchResultsPage,
    props: true,
    meta: { title: (route) => `${route.params.query} | Khaganate` },
  },
  {
    path: "/tasks",
    name: "tasks",
    component: TaskListPage,
    meta: { title: "Tasks | Khaganate" },
  },
  {
    path: "/tasks/:id(\\d+)",
    name: "task",
    component: TaskDetailPage,
    props: (route) => ({ id: parseInt(route.params.id) }),
  },
  {
    path: "/travel",
    name: "travel",
    component: TravelMapPage,
    meta: { title: "Travel | Khaganate" },
  },
  {
    path: "/travel/:year(\\d+)",
    name: "travel-year",
    component: TravelMapPage,
    props: (route) => ({ year: parseInt(route.params.year) }),
    meta: { title: (route) => `Travel, ${route.params.year} | Khaganate` },
  },
  {
    path: "*",
    component: NotFoundPage,
  },
];

const router = new VueRouter({
  mode: "history",
  routes,
});

// Set the page title, courtesy of https://stackoverflow.com/questions/51639850/
router.afterEach((to) => {
  Vue.nextTick(() => {
    if (!to.meta.title) {
      document.title = "Khaganate";
    } else if (isString(to.meta.title)) {
      document.title = to.meta.title;
    } else {
      // Document title is a function.
      document.title = to.meta.title(to);
    }
  });
});

// Third-party plug-ins
Vue.use(BootstrapVue);
Vue.use(BootstrapVueIcons);
Vue.use(IconsPlugin);
Vue.use(VueRouter);

// Custom Khaganate plug-ins
Vue.use(plugins.ApiPlugin);
Vue.use(plugins.DatabasePlugin);
Vue.use(plugins.PopupPlugin);

Vue.mixin({
  methods: {
    today() {
      return DateTime.local();
    },

    todayAdjusted() {
      const today = DateTime.local();
      return today.hour < 5 ? today.minus({ days: 1 }) : today;
    },
  },
});

Vue.component("DateLink", DateLink);
Vue.component("LoadingBox", LoadingBox);
Vue.component("MarkdownBlock", MarkdownBlock);
Vue.component("MarkdownInline", MarkdownInline);
Vue.component("ModalForm", ModalForm);
Vue.component("MonthNav", MonthNav);
Vue.component("Select2", Select2);

Vue.filter("commas", formatIntegerWithCommas);
Vue.filter("date", formatDate);
Vue.filter("pluralize", pluralize);
Vue.filter("usd", formatDollarAmount);

Vue.config.errorHandler = (err, vm, info) => {
  popupService.popup("JavaScript error: " + err, { danger: true });
  console.error(err);
  console.error("Vue component:", vm);
  console.error("Vue info:", info);
};

AppComponent.router = router;
const app = new Vue(AppComponent);
app.$mount("#app");
