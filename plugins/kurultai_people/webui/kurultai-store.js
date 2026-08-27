import { createStore } from "/js/AlpineStore.js";
import { callJsonApi } from "/js/api.js";
import {
  toastFrontendError,
  toastFrontendSuccess,
} from "/components/notifications/notification-store.js";

const API_TEST = "/plugins/kurultai_people/test_connection";
const API_SEARCH = "/plugins/kurultai_people/search";

export const store = createStore("kurultaiPeopleStore", {
  testing: false,
  searching: false,
  query: "",
  hits: [],
  whoKnows: [],

  async testConnection() {
    this.testing = true;
    try {
      const result = await callJsonApi(API_TEST, {});
      if (result?.ok === false) {
        toastFrontendError(result.error || "Connection test failed", "Kurultai People");
        return;
      }
      const count = Array.isArray(result?.sample?.hits) ? result.sample.hits.length : 0;
      toastFrontendSuccess(`Kurultai connected (${count} sample hits)`, "Kurultai People");
    } catch (error) {
      toastFrontendError(error?.message || "Connection test failed", "Kurultai People");
    } finally {
      this.testing = false;
    }
  },

  async runSearch() {
    const query = (this.query || "").trim();
    if (!query) {
      toastFrontendError("Enter a search query", "Kurultai People");
      return;
    }
    this.searching = true;
    try {
      const result = await callJsonApi(API_SEARCH, { query });
      if (result?.error) {
        toastFrontendError(result.error, "Kurultai People");
        this.hits = [];
        this.whoKnows = [];
        return;
      }
      this.hits = Array.isArray(result?.hits) ? result.hits : [];
      this.whoKnows = Array.isArray(result?.who_knows) ? result.who_knows : [];
    } catch (error) {
      toastFrontendError(error?.message || "Search failed", "Kurultai People");
    } finally {
      this.searching = false;
    }
  },

  onOpen() {},
  cleanup() {
    this.hits = [];
    this.whoKnows = [];
  },
});
