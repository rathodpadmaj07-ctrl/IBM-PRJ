import React, { useState } from "react";

function today() {
  return new Date().toISOString().slice(0, 10);
}

export function CaptureModal({ spaces, onClose, onSave, disabled }) {
  const [form, setForm] = useState({
    title: "",
    type: "task",
    spaceId: spaces[0]?.id || "",
    due: today(),
    time: "",
    priority: "medium",
    notes: ""
  });

  const set = (key, val) => setForm(f => ({ ...f, [key]: val }));

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="d-flex align-items-center justify-content-between mb-3">
          <h3 className="m-0 fs-5 fw-bold">Quick Capture</h3>
          <button className="icon-btn" onClick={onClose}><i className="bi bi-x-lg" /></button>
        </div>

        <form onSubmit={e => { e.preventDefault(); if (form.title.trim()) onSave(form); }}>
          <div className="mb-3">
            <label className="form-label fw-semibold">What is on your mind?</label>
            <input
              autoFocus
              className="form-control form-control-lg"
              placeholder="e.g. Prepare lecture notes for Monday"
              value={form.title}
              onChange={e => set("title", e.target.value)}
              required
            />
          </div>

          <div className="row g-2 mb-3">
            <div className="col-6">
              <label className="form-label small text-secondary">Type</label>
              <select className="form-select" value={form.type} onChange={e => set("type", e.target.value)}>
                <option value="task">Task</option>
                <option value="idea">Idea</option>
                <option value="schedule">Schedule</option>
              </select>
            </div>
            <div className="col-6">
              <label className="form-label small text-secondary">Space</label>
              <select className="form-select" value={form.spaceId} onChange={e => set("spaceId", e.target.value)}>
                {spaces.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
            </div>
            <div className="col-6">
              <label className="form-label small text-secondary">Due Date</label>
              <input type="date" className="form-control" value={form.due} onChange={e => set("due", e.target.value)} />
            </div>
            <div className="col-6">
              <label className="form-label small text-secondary">Priority</label>
              <select className="form-select" value={form.priority} onChange={e => set("priority", e.target.value)}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>

          <div className="mb-4">
            <label className="form-label small text-secondary">Notes (Optional)</label>
            <textarea className="form-control" rows="2" value={form.notes} onChange={e => set("notes", e.target.value)} />
          </div>

          <div className="d-flex justify-content-end gap-2">
            <button type="button" className="btn btn-light rounded-pill px-4" onClick={onClose}>Cancel</button>
            <button className="btn btn-dark rounded-pill px-4" disabled={disabled}>Create Item</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export function EditModal({ item, spaces, onClose, onSave, onDelete, disabled }) {
  const [form, setForm] = useState({ ...item });
  const set = (key, val) => setForm(f => ({ ...f, [key]: val }));

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="d-flex align-items-center justify-content-between mb-3">
          <h3 className="m-0 fs-5 fw-bold">Edit Item</h3>
          <button className="icon-btn" onClick={onClose}><i className="bi bi-x-lg" /></button>
        </div>

        <form onSubmit={e => { e.preventDefault(); if (form.title.trim()) onSave(form); }}>
          <div className="mb-3">
            <label className="form-label fw-semibold">Title</label>
            <input
              className="form-control"
              value={form.title}
              onChange={e => set("title", e.target.value)}
              required
            />
          </div>

          <div className="row g-2 mb-3">
            <div className="col-6">
              <label className="form-label small text-secondary">Type</label>
              <select className="form-select" value={form.type} onChange={e => set("type", e.target.value)}>
                <option value="task">Task</option>
                <option value="idea">Idea</option>
                <option value="schedule">Schedule</option>
              </select>
            </div>
            <div className="col-6">
              <label className="form-label small text-secondary">Space</label>
              <select className="form-select" value={form.spaceId} onChange={e => set("spaceId", e.target.value)}>
                {spaces.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
            </div>
            <div className="col-6">
              <label className="form-label small text-secondary">Due Date</label>
              <input type="date" className="form-control" value={form.due || ""} onChange={e => set("due", e.target.value)} />
            </div>
            <div className="col-6">
              <label className="form-label small text-secondary">Priority</label>
              <select className="form-select" value={form.priority} onChange={e => set("priority", e.target.value)}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>

          <div className="mb-4">
            <label className="form-label small text-secondary">Notes</label>
            <textarea className="form-control" rows="3" value={form.notes || ""} onChange={e => set("notes", e.target.value)} />
          </div>

          <div className="d-flex justify-content-between">
            <button type="button" className="btn btn-outline-danger rounded-pill px-3" onClick={onDelete}>Delete</button>
            <div className="d-flex gap-2">
              <button type="button" className="btn btn-light rounded-pill px-4" onClick={onClose}>Cancel</button>
              <button className="btn btn-dark rounded-pill px-4" disabled={disabled}>Save Changes</button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

export function SpaceModal({ onClose, onSave, disabled }) {
  const [name, setName] = useState("");
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="d-flex align-items-center justify-content-between mb-3">
          <h3 className="m-0 fs-5 fw-bold">Create Space</h3>
          <button className="icon-btn" onClick={onClose}><i className="bi bi-x-lg" /></button>
        </div>
        <form onSubmit={e => { e.preventDefault(); if (name.trim()) onSave(name); }}>
          <div className="mb-4">
            <label className="form-label small text-secondary">Space Name</label>
            <input autoFocus className="form-control" placeholder="e.g. Research & Writing" value={name} onChange={e => setName(e.target.value)} required />
          </div>
          <div className="d-flex justify-content-end gap-2">
            <button type="button" className="btn btn-light rounded-pill px-4" onClick={onClose}>Cancel</button>
            <button className="btn btn-dark rounded-pill px-4" disabled={disabled}>Create Space</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export function SpaceEditModal({ space, onClose, onSave, onDelete, disabled }) {
  const [name, setName] = useState(space.name);
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="d-flex align-items-center justify-content-between mb-3">
          <h3 className="m-0 fs-5 fw-bold">Edit Space</h3>
          <button className="icon-btn" onClick={onClose}><i className="bi bi-x-lg" /></button>
        </div>
        <form onSubmit={e => { e.preventDefault(); if (name.trim()) onSave(space.id, name); }}>
          <div className="mb-4">
            <label className="form-label small text-secondary">Space Name</label>
            <input autoFocus className="form-control" value={name} onChange={e => setName(e.target.value)} required />
          </div>
          <div className="d-flex justify-content-between">
            <button type="button" className="btn btn-outline-danger rounded-pill px-3" onClick={() => onDelete(space.id)}>Delete</button>
            <div className="d-flex gap-2">
              <button type="button" className="btn btn-light rounded-pill px-4" onClick={onClose}>Cancel</button>
              <button className="btn btn-dark rounded-pill px-4" disabled={disabled}>Save Changes</button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
