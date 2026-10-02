import React from "react";

export function Topbar({
  active,
  pageTitle,
  dark,
  setDark,
  onOpenCommand,
  unreadCount = 0,
  onToggleNotifications,
  isNotificationOpen
}) {
  const currentDate = new Date().toLocaleDateString("en-IN", {
    weekday: "long",
    day: "numeric",
    month: "long"
  }).toUpperCase();

  const isMac = typeof navigator !== "undefined" && navigator.platform
    ? navigator.platform.toUpperCase().indexOf("MAC") >= 0
    : false;
  const kbdShortcut = isMac ? "⌘ K" : "Ctrl K";

  const formattedUnread = unreadCount > 9 ? "9+" : unreadCount;

  return (
    <header className="topbar">
      <div>
        <div className="eyebrow">{currentDate}</div>
        <h1>{active === "Dashboard" ? "Good afternoon, Padmaj." : pageTitle}</h1>
      </div>
      <div className="top-actions">
        <button className="search-btn" onClick={() => onOpenCommand(true)}>
          <i className="bi bi-search" />
          <span>Search command...</span>
          <span className="kbd-shortcut">{kbdShortcut}</span>
        </button>

        {/* Notification Bell Button */}
        <div className="position-relative">
          <button
            className={`icon-btn ${isNotificationOpen ? "active" : ""}`}
            onClick={onToggleNotifications}
            title="Notifications"
            aria-label="Notifications"
          >
            <i className="bi bi-bell" />
            {unreadCount > 0 && <span className="bell-badge">{formattedUnread}</span>}
          </button>
        </div>

        <button
          className="icon-btn"
          onClick={() => setDark(!dark)}
          title="Toggle theme"
          aria-label="Toggle theme"
        >
          <i className={`bi ${dark ? "bi-sun" : "bi-moon"}`} />
        </button>

        <div className="avatar">PR</div>
      </div>
    </header>
  );
}
