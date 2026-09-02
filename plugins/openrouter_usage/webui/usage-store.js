import { createStore } from "/js/AlpineStore.js";
import { callJsonApi } from "/js/api.js";
import {
  toastFrontendError,
  toastFrontendSuccess,
} from "/components/notifications/notification-store.js";

const API_OVERVIEW = "/plugins/openrouter_usage/overview";
const API_KEYS = "/plugins/openrouter_usage/keys_list";
const API_REFRESH = "/plugins/openrouter_usage/refresh";
const VIEW_KEY = "openrouter_usage_view";

export const store = createStore("openrouterUsageStore", {
  loading: false,
  overview: null,
  availableKeys: [],
  pollTimer: null,
  view: localStorage.getItem(VIEW_KEY) || "simple",

  get emptyState() {
    return this.overview?.empty_state || null;
  },

  get hasData() {
    return !!this.overview?.ok;
  },

  get summary() {
    return this.overview?.summary || {};
  },

  get totals() {
    return this.overview?.totals || {};
  },

  get credits() {
    return this.overview?.credits || {};
  },

  get summaryLine() {
    const totals = this.totals;
    return `${totals.usd_label || "$0"} · last 30d`;
  },

  get creditLine() {
    const c = this.credits;
    if (!c) return "";
    const balance = c.balance_label || "—";
    const lifetime = c.usage_label || "—";
    return `Balance ${balance} · Lifetime ${lifetime}`;
  },

  get mtdLine() {
    const s = this.summary;
    return `MTD ${s.mtd_label || "$0"}`;
  },

  get widgetLabel() {
    if (this.loading) return "…";
    return this.totals?.usd_label || "OR";
  },

  get topKeys() {
    return Array.isArray(this.overview?.top_keys) ? this.overview.top_keys : [];
  },

  get topModels() {
    return Array.isArray(this.overview?.top_models) ? this.overview.top_models : [];
  },

  get topProviders() {
    return Array.isArray(this.overview?.top_providers) ? this.overview.top_providers : [];
  },

  get allModels() {
    return Array.isArray(this.overview?.models) ? this.overview.models : [];
  },

  get allProviders() {
    return Array.isArray(this.overview?.providers) ? this.overview.providers : [];
  },

  get perKey() {
    return Array.isArray(this.overview?.per_key) ? this.overview.per_key : [];
  },

  get daily() {
    return Array.isArray(this.overview?.daily) ? this.overview.daily : [];
  },

  get showTokenCounts() {
    return !!this.overview?.settings?.show_token_counts;
  },

  get asOfLabel() {
    if (!this.overview?.as_of) return "";
    try {
      return new Date(this.overview.as_of).toLocaleString();
    } catch {
      return this.overview.as_of;
    }
  },

  get allKeyColors() {
    return this.colorMapFor(this.perKey.map((row) => row.label));
  },

  setView(mode) {
    this.view = mode === "detailed" ? "detailed" : "simple";
    localStorage.setItem(VIEW_KEY, this.view);
  },

  async fetchOverview({ force = false } = {}) {
    this.loading = true;
    try {
      this.overview = await callJsonApi(force ? API_REFRESH : API_OVERVIEW, force ? { force: true } : {});
    } catch (error) {
      toastFrontendError(error?.message || "Failed to load OpenRouter usage", "OpenRouter Usage");
    } finally {
      this.loading = false;
    }
  },

  async fetchKeys() {
    try {
      const result = await callJsonApi(API_KEYS, {});
      if (!result?.ok) {
        toastFrontendError(result?.error || "Could not list keys", "OpenRouter Usage");
        return;
      }
      this.availableKeys = Array.isArray(result.keys) ? result.keys : [];
      toastFrontendSuccess(`Loaded ${this.availableKeys.length} keys`, "OpenRouter Usage");
    } catch (error) {
      toastFrontendError(error?.message || "Could not list keys", "OpenRouter Usage");
    }
  },

  toggleWatch(hashPrefix, config) {
    if (!config || !hashPrefix) return;
    const list = Array.isArray(config.watched_key_hashes) ? [...config.watched_key_hashes] : [];
    const index = list.indexOf(hashPrefix);
    if (index >= 0) list.splice(index, 1);
    else list.push(hashPrefix);
    config.watched_key_hashes = list;
  },

  isWatched(hashPrefix, config) {
    const list = config?.watched_key_hashes;
    return Array.isArray(list) && list.includes(hashPrefix);
  },

  startPolling() {
    this.stopPolling();
    const minutes = Number(this.overview?.settings?.refresh_interval_minutes || 5);
    const ms = Math.max(1, minutes) * 60 * 1000;
    this.pollTimer = window.setInterval(() => this.fetchOverview(), ms);
  },

  stopPolling() {
    if (this.pollTimer) {
      window.clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
  },

  onOpen() {
    this.fetchOverview().then(() => this.startPolling());
  },

  cleanup() {
    this.stopPolling();
  },

  formatNumber(n) {
    return Number(n || 0).toLocaleString();
  },

  formatUsd(value) {
    const n = Number(value || 0);
    if (n < 0.01) return `$${n.toFixed(4)}`;
    if (n < 1) return `$${n.toFixed(3)}`;
    return `$${n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  },

  maxBar(values, field = "usd") {
    const nums = values.map((item) => Number(item[field]) || 0);
    return Math.max(...nums, 0.0001);
  },

  barWidth(value, max) {
    const pct = Math.min(100, (Number(value || 0) / max) * 100);
    return `${pct}%`;
  },

  pctOf(value, total) {
    const t = Number(total || 0);
    if (!t) return "0%";
    return `${Math.min(100, Math.round((Number(value || 0) / t) * 100))}%`;
  },

  colorFor(index) {
    const palette = [
      "#7bdff9",
      "#f7b267",
      "#b2f7ef",
      "#f79d84",
      "#87ceeb",
      "#ffdfba",
      "#a0c4ff",
      "#ffc6ff",
      "#9bf6ff",
      "#fdffb6",
    ];
    return palette[index % palette.length];
  },

  colorMapFor(labels) {
    const map = {};
    (labels || []).forEach((label, i) => {
      map[label] = this.colorFor(i);
    });
    return map;
  },

  stackedSegments(day, colorMap) {
    const byKey = day.by_key || {};
    const total = Number(day.total) || Object.values(byKey).reduce((a, b) => a + b, 0);
    const labels = Object.keys(byKey).sort();
    let left = 0;
    return labels.map((label) => {
      const value = Number(byKey[label]) || 0;
      const pct = total ? (value / total) * 100 : 0;
      const seg = {
        label,
        value,
        color: colorMap?.[label] || this.colorFor(0),
        pct,
        left,
        total,
      };
      left += pct;
      return seg;
    });
  },
});
