import { createStore } from "/js/AlpineStore.js";
import { callJsonApi } from "/js/api.js";
import {
  toastFrontendError,
  toastFrontendSuccess,
} from "/components/notifications/notification-store.js";

const API_TEST = "/plugins/kurultai_people/test_connection";
const API_SEARCH = "/plugins/kurultai_people/search";
const RECENTS_KEY = "kurultai_recent_searches";
const RECENTS_MAX = 10;

export const store = createStore("kurultaiPeopleStore", {
  testing: false,
  searching: false,
  connection: "unknown", // unknown | ok | failed
  connectionNote: "",
  query: "",
  scope: "",
  source: "",
  searched: false,
  hits: [],
  whoKnows: [],
  error: null,
  recents: JSON.parse(localStorage.getItem(RECENTS_KEY) || "[]"),
  _searchSeq: 0,

  get hasResults() {
    return this.hits.length > 0;
  },

  get connectionPill() {
    if (this.connection === "ok") return { cls: "good", label: "Connected" };
    if (this.connection === "failed") return { cls: "bad", label: "Unreachable" };
    return { cls: "", label: "Not tested" };
  },

  _pushRecent(query) {
    const q = (query || "").trim();
    if (!q) return;
    const list = [q, ...this.recents.filter((r) => r !== q)].slice(0, RECENTS_MAX);
    this.recents = list;
    localStorage.setItem(RECENTS_KEY, JSON.stringify(list));
  },

  useRecent(q) {
    this.query = q;
    this.runSearch();
  },

  clearRecents() {
    this.recents = [];
    localStorage.removeItem(RECENTS_KEY);
  },

  async testConnection() {
    this.testing = true;
    try {
      const result = await callJsonApi(API_TEST, {});
      if (result?.ok === false) {
        this.connection = "failed";
        this.connectionNote = result.error || "Connection test failed";
        toastFrontendError(this.connectionNote, "Kurultai People");
        return;
      }
      const count = Array.isArray(result?.sample?.hits) ? result.sample.hits.length : 0;
      this.connection = "ok";
      this.connectionNote = `${count} sample hits`;
      toastFrontendSuccess(`Kurultai connected (${count} sample hits)`, "Kurultai People");
    } catch (error) {
      this.connection = "failed";
      this.connectionNote = error?.message || "Connection test failed";
      toastFrontendError(this.connectionNote, "Kurultai People");
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
    const seq = ++this._searchSeq;
    this.searching = true;
    this.searched = true;
    this.error = null;
    try {
      const payload = { query };
      if (this.scope) payload.scope = this.scope;
      if (this.source) payload.source = this.source;
      const result = await callJsonApi(API_SEARCH, payload);
      if (seq !== this._searchSeq) return; // stale response
      if (result?.error || result?.ok === false) {
        this.error = result?.error || "Search failed";
        toastFrontendError(this.error, "Kurultai People");
        this.hits = [];
        this.whoKnows = [];
        return;
      }
      this.hits = Array.isArray(result?.hits) ? result.hits : [];
      this.whoKnows = Array.isArray(result?.who_knows) ? result.who_knows : [];
      this._pushRecent(query);
    } catch (error) {
      if (seq !== this._searchSeq) return;
      this.error = error?.message || "Search failed";
      toastFrontendError(this.error, "Kurultai People");
    } finally {
      if (seq === this._searchSeq) this.searching = false;
    }
  },

  scorePct(score) {
    const n = Number(score);
    if (!Number.isFinite(n) || n <= 0) return 0;
    return Math.min(100, Math.round(n * 100));
  },

  async copyCitation(hit) {
    const text = `${hit.title}\nsource: ${hit.source} / ${hit.source_id}\n${hit.snippet}`;
    try {
      await navigator.clipboard.writeText(text);
      toastFrontendSuccess("Citation copied", "Kurultai People");
    } catch {
      toastFrontendError("Clipboard unavailable", "Kurultai People");
    }
  },

  onOpen() {},
  cleanup() {
    this.hits = [];
    this.whoKnows = [];
    this.searched = false;
    this.error = null;
  },
});
