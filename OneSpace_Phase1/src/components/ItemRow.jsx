import React from "react";
import { formatFriendlyDate } from "../utils/dateUtils.js";

export function ItemRow({ item, spaces, onToggle, onOpenDrawer, onEdit, onDelete }) {
  const spaceName = spaces.find(s => s.id === item.spaceId)?.name || "Unsorted";
  const priority = item.priority || "medium";

  return (
    <div className={`item-row ${item.completed ? "completed" : ""}`}>
      <button
        className={`check-btn ${item.completed ? "checked" : ""}`}
        onClick={(e) => {
          e.stopPropagation();
          onToggle();
        }}
        title={item.completed ? "Mark incomplete" : "Mark complete"}
        aria-label={item.completed ? "Mark incomplete" : "Mark complete"}
      >
        {item.completed && (
          <svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M13.3333 4L6 11.3333L2.66667 8" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        )}
      </button>

      <div
        className="item-main"
        onClick={() => onOpenDrawer(item)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            onOpenDrawer(item);
          }
        }}
      >
        <div className="item-title">{item.title}</div>
        <div className="item-meta">
          <span className={`type-pill type-${item.type}`}>{item.type}</span>
          <span className="space-meta-tag">
            <i className="bi bi-folder2-open me-1" />
            <span className="space-name-text">{spaceName}</span>
          </span>
          {item.due && (
            <span className="due-meta-tag">
              <i className="bi bi-calendar3 me-1" />
              {formatFriendlyDate(item.due, item.time)}
            </span>
          )}
          <span className={`chip-priority chip-priority-${priority}`}>
            {priority} priority
          </span>
        </div>
      </div>

      <div className="item-actions" onClick={(e) => e.stopPropagation()}>
        <button className="action-btn view-btn" title="View details" aria-label="View details" onClick={() => onOpenDrawer(item)}>
          <i className="bi bi-eye" />
        </button>
        <button className="action-btn edit-btn" title="Edit" aria-label="Edit" onClick={() => onEdit(item)}>
          <i className="bi bi-pencil" />
        </button>
        <button className="action-btn delete-btn" title="Delete" aria-label="Delete" onClick={() => onDelete(item.id)}>
          <i className="bi bi-trash3" />
        </button>
      </div>
    </div>
  );
}
