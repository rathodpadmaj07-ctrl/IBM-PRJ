import React from "react";
import { formatFriendlyDate } from "../utils/dateUtils.js";

export function DashboardView({ stats, items, onAdd, onOpenItem }) {
  const attentionItem = items.find(
    item => !item.completed && (item.priority === "high" || (item.due && item.due < new Date().toISOString().slice(0, 10)))
  );

  return (
    <div className="dashboard-block">
      <div className="hero-row">
        <div>
          <h2>Good afternoon, Padmaj.</h2>
          <p className="hero-status-line">
            Your focus today · {String(stats.total).padStart(2, "0")} tasks · {String(stats.completed).padStart(2, "0")} completed · {String(stats.pending).padStart(2, "0")} pending · {String(stats.high).padStart(2, "0")} high priority
          </p>
        </div>
        <button className="btn-primary-action" onClick={onAdd}>
          <i className="bi bi-plus-lg me-1" /> New item
        </button>
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-icon total"><i className="bi bi-layers" /></div>
          <div>
            <b>{String(stats.total).padStart(2, "0")}</b>
            <span>Total tasks</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon completed"><i className="bi bi-check2-circle" /></div>
          <div>
            <b>{String(stats.completed).padStart(2, "0")}</b>
            <span>Completed</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon pending"><i className="bi bi-hourglass-split" /></div>
          <div>
            <b>{String(stats.pending).padStart(2, "0")}</b>
            <span>Pending</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon high"><i className="bi bi-flag" /></div>
          <div>
            <b>{String(stats.high).padStart(2, "0")}</b>
            <span>High priority</span>
          </div>
        </div>
      </div>

      {attentionItem ? (
        <div className="attention-banner">
          <div>
            <div className="eyebrow attention-eyebrow mb-1">NEEDS ATTENTION</div>
            <h3>{attentionItem.title}</h3>
            <p>
              Due {attentionItem.due ? formatFriendlyDate(attentionItem.due, attentionItem.time) : "Soon"} · {attentionItem.priority.toUpperCase()} PRIORITY
            </p>
          </div>
          <button className="btn-open-details" onClick={() => onOpenItem(attentionItem)}>
            Open details &rarr;
          </button>
        </div>
      ) : (
        <div className="p-4 border rounded-3 text-secondary text-center bg-body-tertiary mb-4">
          <i className="bi bi-check-circle me-2 text-success" /> All caught up! Nothing needs immediate attention.
        </div>
      )}
    </div>
  );
}
