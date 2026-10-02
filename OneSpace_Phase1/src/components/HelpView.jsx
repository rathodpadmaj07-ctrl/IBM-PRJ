import React from "react";

export function HelpView() {
  return (
    <div className="help-page">
      <div className="eyebrow">GUIDE</div>
      <h2 className="fs-3 fw-bold mb-3">How OneSpace Works</h2>
      <p className="lead text-secondary mb-4">
        OneSpace is your calm, personal command center designed for seamless capture, spatial organization, and intelligent focus.
      </p>

      <div className="row g-4">
        <div className="col-md-6">
          <div className="p-4 border rounded-4 bg-body-surface h-100 shadow-sm">
            <div className="fs-3 text-warning mb-2"><i className="bi bi-lightning-charge" /></div>
            <h3 className="fs-5 fw-bold mb-2">1. Quick Capture</h3>
            <p className="text-secondary small m-0">
              Press <kbd className="bg-body-tertiary text-body border px-2 py-1 rounded">⌘K</kbd> anywhere or click <strong>Quick Capture</strong> to immediately record a task, idea, or schedule before it slips away.
            </p>
          </div>
        </div>

        <div className="col-md-6">
          <div className="p-4 border rounded-4 bg-body-surface h-100 shadow-sm">
            <div className="fs-3 text-primary mb-2"><i className="bi bi-folder2-open" /></div>
            <h3 className="fs-5 fw-bold mb-2">2. Spatial Territories</h3>
            <p className="text-secondary small m-0">
              Organize items into distinct life territories like <strong>Personal</strong>, <strong>College</strong>, and <strong>Projects</strong>.
            </p>
          </div>
        </div>

        <div className="col-md-6">
          <div className="p-4 border rounded-4 bg-body-surface h-100 shadow-sm">
            <div className="fs-3 text-danger mb-2"><i className="bi bi-exclamation-circle" /></div>
            <h3 className="fs-5 fw-bold mb-2">3. Needs Attention</h3>
            <p className="text-secondary small m-0">
              The dashboard automatically surfaces high-priority and overdue items into your immediate focus area.
            </p>
          </div>
        </div>

        <div className="col-md-6">
          <div className="p-4 border rounded-4 bg-body-surface h-100 shadow-sm">
            <div className="fs-3 text-success mb-2"><i className="bi bi-layout-sidebar-reverse" /></div>
            <h3 className="fs-5 fw-bold mb-2">4. Detail Drawer</h3>
            <p className="text-secondary small m-0">
              Click any item to open the slide-over detail drawer for deep inspection, notes editing, and instant status updates.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
