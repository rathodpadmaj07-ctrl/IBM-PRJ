import React from "react";

export function Sidebar({ active, setActive, spaces, stats, onOpenQuickCapture, onOpenCreateSpace, onOpenEditSpace, onDeleteSpace }) {
  const isMac = typeof navigator !== "undefined" && navigator.platform
    ? navigator.platform.toUpperCase().indexOf("MAC") >= 0
    : false;
  const kbdShortcut = isMac ? "⌘ K" : "Ctrl K";

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark"><i className="bi bi-layers-fill" /></div>
        <span>OneSpace</span>
      </div>

      <button className="quick-capture-btn" onClick={onOpenQuickCapture}>
        <span><i className="bi bi-plus-lg me-2" /> Quick Capture</span>
        <span className="kbd-shortcut">{kbdShortcut}</span>
      </button>

      <div className="nav-section">
        <div className="nav-label">WORKSPACE</div>
        {[
          ["Dashboard", "bi-grid-1x2-fill"],
          ["Needs Attention", "bi-exclamation-circle"],
          ["Today", "bi-calendar3"],
          ["Upcoming", "bi-calendar-week"],
          ["Ideas", "bi-lightbulb"]
        ].map(([label, icon]) => (
          <button
            key={label}
            className={`side-link ${active === label ? "active" : ""}`}
            onClick={() => setActive(label)}
          >
            <i className={`bi ${icon}`} />
            <span>{label}</span>
            {label === "Needs Attention" && stats.attention > 0 && (
              <small className="badge-count">{stats.attention}</small>
            )}
          </button>
        ))}
      </div>

      <div className="nav-section spaces-section">
        <div className="space-heading">
          <span className="nav-label mb-0">SPACES</span>
          <button className="icon-btn" title="Create Space" onClick={onOpenCreateSpace}>
            <i className="bi bi-plus" />
          </button>
        </div>
        {spaces.map(space => (
          <div className="space-nav-row" key={space.id}>
            <button
              className={`side-link ${active === `space:${space.id}` ? "active" : ""}`}
              onClick={() => setActive(`space:${space.id}`)}
            >
              <i className={`bi ${space.icon || "bi-folder"}`} />
              <span className="space-link-title">{space.name}</span>
              <small className="badge-count">{space.count}</small>
            </button>
            <button
              className="icon-btn space-action"
              title={`Edit ${space.name}`}
              onClick={() => onOpenEditSpace(space)}
            >
              <i className="bi bi-pencil" />
            </button>
            <button
              className="icon-btn space-action danger-hover"
              title={`Delete ${space.name}`}
              onClick={() => onDeleteSpace(space.id)}
            >
              <i className="bi bi-trash3" />
            </button>
          </div>
        ))}
      </div>

      <div className="sidebar-bottom">
        <button className={`side-link ${active === "Settings" ? "active" : ""}`} onClick={() => setActive("Settings")}>
          <i className="bi bi-gear" /><span>Settings</span>
        </button>
        <button className={`side-link ${active === "Help" ? "active" : ""}`} onClick={() => setActive("Help")}>
          <i className="bi bi-question-circle" /><span>Help</span>
        </button>
      </div>
    </aside>
  );
}
