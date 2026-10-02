import React from "react";
import { formatFriendlyDate } from "../utils/dateUtils.js";

export function ItemDrawer({ item, spaces, onClose, onToggleComplete, onDelete, onEdit }) {
  if (!item) return null;

  const spaceName = spaces.find(s => s.id === item.spaceId)?.name || "Unsorted";
  const priority = item.priority || "medium";

  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <div className="drawer-card" onClick={e => e.stopPropagation()}>
        <div className="drawer-header">
          <div className="eyebrow">ITEM DETAILS</div>
          <button className="icon-btn" onClick={onClose} title="Close">
            <i className="bi bi-x-lg" />
          </button>
        </div>
        <div className="drawer-body">
          <div className="d-flex align-items-center gap-2 mb-3">
            <button
              className={`check-btn ${item.completed ? "checked" : ""}`}
              onClick={() => onToggleComplete(item)}
              title={item.completed ? "Mark incomplete" : "Mark complete"}
            >
              {item.completed && (
                <svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M13.3333 4L6 11.3333L2.66667 8" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              )}
            </button>
            <h2 className="m-0 fs-4 fw-bold">{item.title}</h2>
          </div>

          <div className="d-flex flex-wrap gap-2 mb-4">
            <span className={`type-pill type-${item.type}`}>{item.type}</span>
            <span className="badge space-badge border">
              <i className="bi bi-folder2-open me-1" /> {spaceName}
            </span>
            <span className={`chip-priority chip-priority-${priority}`}>
              {priority} priority
            </span>
            {item.due && (
              <span className="badge space-badge border">
                <i className="bi bi-calendar3 me-1" /> Due: {formatFriendlyDate(item.due, item.time)}
              </span>
            )}
          </div>

          <div className="mb-4">
            <label className="nav-label">NOTES & DESCRIPTION</label>
            <p className="p-3 border rounded-3 drawer-notes text-secondary">
              {item.notes || "No notes provided for this item."}
            </p>
          </div>
        </div>

        <div className="d-flex gap-2 border-top pt-3">
          <button className="btn btn-outline-secondary rounded-pill flex-fill" onClick={() => onEdit(item)}>
            <i className="bi bi-pencil me-2" /> Edit Item
          </button>
          <button className="btn btn-outline-danger rounded-pill" onClick={() => onDelete(item.id)}>
            <i className="bi bi-trash3" />
          </button>
        </div>
      </div>
    </div>
  );
}
