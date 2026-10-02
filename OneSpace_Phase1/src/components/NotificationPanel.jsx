import React from "react";

function formatTimestamp(isoString) {
  if (!isoString) return "";
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);

  if (diffMins < 2) return "Just now";
  if (diffMins < 60) return `${diffMins} mins ago`;
  if (diffHours < 24) return `${diffHours} ${diffHours === 1 ? "hour" : "hours"} ago`;
  return date.toLocaleDateString("en-IN", { month: "short", day: "numeric" });
}

function getCategoryIcon(type) {
  switch (type) {
    case "TASK_DUE_SOON":
      return <i className="bi bi-clock-history notif-icon-info" />;
    case "TASK_DUE_TODAY":
      return <i className="bi bi-calendar-event notif-icon-info" />;
    case "TASK_OVERDUE":
      return <i className="bi bi-exclamation-triangle-fill notif-icon-danger" />;
    case "HIGH_PRIORITY":
      return <i className="bi bi-flag-fill notif-icon-danger" />;
    case "TASK_COMPLETED":
      return <i className="bi bi-check-circle-fill notif-icon-success" />;
    case "NEW_SPACE":
      return <i className="bi bi-folder-plus notif-icon-accent" />;
    default:
      return <i className="bi bi-bell text-secondary" />;
  }
}

export function NotificationPanel({
  isOpen,
  onClose,
  notifications,
  onMarkRead,
  onMarkAllRead,
  onDeleteNotification,
  onClearAll,
  onSelectTaskItem
}) {
  if (!isOpen) return null;

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="notification-panel-popover" onClick={e => e.stopPropagation()}>
      <div className="notification-panel-header">
        <div className="d-flex align-items-center gap-2">
          <h3 className="m-0 fs-6 fw-bold">Notifications</h3>
          {unreadCount > 0 && <span className="badge-unread-count">{unreadCount}</span>}
        </div>
        {unreadCount > 0 && (
          <button className="text-btn small" onClick={onMarkAllRead}>
            Mark all as read
          </button>
        )}
      </div>

      <div className="notification-panel-body">
        {notifications.length > 0 ? (
          notifications.map(n => (
            <div
              key={n.id}
              className={`notification-item ${!n.read ? "unread" : ""}`}
              onClick={() => {
                onMarkRead(n.id);
                if (n.itemId) onSelectTaskItem(n.itemId);
              }}
            >
              <div className="notification-icon">{getCategoryIcon(n.type)}</div>
              <div className="notification-content">
                <div className="d-flex align-items-center justify-content-between mb-1">
                  <div className="notification-title">{n.title}</div>
                  <span className="notification-time">{formatTimestamp(n.createdAt)}</span>
                </div>
                {n.message && <div className="notification-message">{n.message}</div>}
              </div>
              <button
                className="notification-dismiss"
                title="Dismiss"
                onClick={e => {
                  e.stopPropagation();
                  onDeleteNotification(n.id);
                }}
              >
                &times;
              </button>
            </div>
          ))
        ) : (
          <div className="notification-empty">
            <i className="bi bi-bell fs-2 d-block text-tertiary mb-2" />
            <h4 className="fs-6 fw-bold mb-1">You're all caught up</h4>
            <p className="small text-secondary m-0">No new notifications.</p>
          </div>
        )}
      </div>

      {notifications.length > 0 && (
        <div className="notification-panel-footer">
          <button className="text-btn text-secondary small" onClick={onClearAll}>
            Clear all
          </button>
        </div>
      )}
    </div>
  );
}
