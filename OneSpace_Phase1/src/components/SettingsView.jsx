import React from "react";

export function SettingsView({
  dark,
  setDark,
  source,
  onReloadApi,
  notifPrefs = { dueSoon: true, dueToday: true, overdue: true, completed: true, timing: "24h" },
  setNotifPrefs
}) {
  const updatePref = (key, val) => {
    if (setNotifPrefs) {
      setNotifPrefs(prev => ({ ...prev, [key]: val }));
    }
  };

  return (
    <div className="settings-page">
      <div className="eyebrow">PREFERENCES</div>
      <h2 className="fs-3 fw-bold mb-4">Settings</h2>

      {/* Notifications & Reminders Preferences */}
      <div className="card mb-4 p-4 border-0 shadow-sm surface-elevated">
        <h3 className="fs-5 fw-bold mb-3">Notifications & Reminders</h3>
        <div className="row g-3 mb-4">
          <div className="col-sm-6">
            <div className="form-check form-switch">
              <input
                className="form-check-input"
                type="checkbox"
                id="pref-due-soon"
                checked={notifPrefs.dueSoon}
                onChange={e => updatePref("dueSoon", e.target.checked)}
              />
              <label className="form-check-label fw-semibold" htmlFor="pref-due-soon">Due soon</label>
            </div>
          </div>

          <div className="col-sm-6">
            <div className="form-check form-switch">
              <input
                className="form-check-input"
                type="checkbox"
                id="pref-due-today"
                checked={notifPrefs.dueToday}
                onChange={e => updatePref("dueToday", e.target.checked)}
              />
              <label className="form-check-label fw-semibold" htmlFor="pref-due-today">Due today</label>
            </div>
          </div>

          <div className="col-sm-6">
            <div className="form-check form-switch">
              <input
                className="form-check-input"
                type="checkbox"
                id="pref-overdue"
                checked={notifPrefs.overdue}
                onChange={e => updatePref("overdue", e.target.checked)}
              />
              <label className="form-check-label fw-semibold" htmlFor="pref-overdue">Overdue</label>
            </div>
          </div>


        </div>

        <h4 className="fs-6 fw-bold mb-2">Reminder timing</h4>
        <div className="d-flex flex-wrap gap-4">
          <label className="form-check-label small text-secondary">
            <input
              type="radio"
              name="timing"
              value="24h"
              checked={notifPrefs.timing === "24h"}
              onChange={e => updatePref("timing", e.target.value)}
              className="form-check-input me-1"
            /> 24 hours before
          </label>
          <label className="form-check-label small text-secondary">
            <input
              type="radio"
              name="timing"
              value="2h"
              checked={notifPrefs.timing === "2h"}
              onChange={e => updatePref("timing", e.target.value)}
              className="form-check-input me-1"
            /> 2 hours before
          </label>
          <label className="form-check-label small text-secondary">
            <input
              type="radio"
              name="timing"
              value="30m"
              checked={notifPrefs.timing === "30m"}
              onChange={e => updatePref("timing", e.target.value)}
              className="form-check-input me-1"
            /> 30 minutes before
          </label>
        </div>
      </div>

      <div className="card mb-4 p-4 border-0 shadow-sm surface-elevated">
        <div className="d-flex align-items-center justify-content-between">
          <div>
            <h3 className="fs-5 fw-bold mb-1">Appearance</h3>
            <p className="text-secondary small m-0">Switch between light (clean slate) and dark (neutral graphite) themes.</p>
          </div>
          <button
            className="btn btn-outline-secondary rounded-pill px-4"
            onClick={() => setDark(!dark)}
          >
            <i className={`bi ${dark ? "bi-sun" : "bi-moon"} me-2`} />
            {dark ? "Light Mode" : "Dark Mode"}
          </button>
        </div>
      </div>

      <div className="card mb-4 p-4 border-0 shadow-sm surface-elevated">
        <div className="d-flex align-items-center justify-content-between">
          <div>
            <h3 className="fs-5 fw-bold mb-1">Data Synchronization</h3>
            <p className="text-secondary small m-0">
              Current storage mode: <span className="badge bg-secondary-subtle text-secondary uppercase ms-1">{source.toUpperCase()}</span>
            </p>
          </div>
          <button
            className="btn btn-outline-dark rounded-pill px-4"
            onClick={onReloadApi}
          >
            <i className="bi bi-arrow-repeat me-2" /> Sync API
          </button>
        </div>
      </div>

      <div className="card p-4 border-0 shadow-sm surface-elevated">
        <h3 className="fs-5 fw-bold mb-2">Keyboard Shortcuts</h3>
        <ul className="list-unstyled text-secondary small m-0">
          <li className="mb-2"><kbd className="bg-body-tertiary text-body border px-2 py-1 rounded">⌘K</kbd> or <kbd className="bg-body-tertiary text-body border px-2 py-1 rounded">Ctrl+K</kbd> — Open Command Palette & Quick Search</li>
          <li className="mb-2"><kbd className="bg-body-tertiary text-body border px-2 py-1 rounded">ESC</kbd> — Close Drawer / Modal / Command Palette</li>
        </ul>
      </div>
    </div>
  );
}
