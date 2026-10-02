import React, { useEffect, useState } from "react";

export function CommandMenu({ isOpen, onClose, items, spaces, onSelectItem, onSelectNav, onToggleDark }) {
  const [query, setQuery] = useState("");

  useEffect(() => {
    function handleKeyDown(e) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        onClose(!isOpen);
      }
      if (e.key === "Escape" && isOpen) {
        onClose(false);
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const filteredItems = items.filter(i => i.title.toLowerCase().includes(query.toLowerCase()));
  const filteredSpaces = spaces.filter(s => s.name.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="command-backdrop" onClick={onClose}>
      <div className="command-modal" onClick={e => e.stopPropagation()}>
        <div className="command-input-wrapper">
          <i className="bi bi-search" />
          <input
            autoFocus
            placeholder="Type a command or search items..."
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
          <span className="kbd-shortcut">ESC</span>
        </div>
        <div className="command-results">
          <div className="nav-label">QUICK ACTIONS</div>
          <div className="command-item" onClick={() => { onToggleDark(); onClose(false); }}>
            <i className="bi bi-moon-stars" /> Toggle Dark / Light Theme
          </div>
          <div className="command-item" onClick={() => { onSelectNav("Dashboard"); onClose(false); }}>
            <i className="bi bi-grid-1x2" /> Go to Dashboard
          </div>
          <div className="command-item" onClick={() => { onSelectNav("Needs Attention"); onClose(false); }}>
            <i className="bi bi-exclamation-circle" /> View Needs Attention
          </div>

          {filteredSpaces.length > 0 && (
            <>
              <div className="nav-label mt-2">SPACES</div>
              {filteredSpaces.map(space => (
                <div key={space.id} className="command-item" onClick={() => { onSelectNav(`space:${space.id}`); onClose(false); }}>
                  <i className={`bi ${space.icon || "bi-folder"}`} /> {space.name} Space
                </div>
              ))}
            </>
          )}

          {filteredItems.length > 0 && (
            <>
              <div className="nav-label mt-2">ITEMS ({filteredItems.length})</div>
              {filteredItems.slice(0, 5).map(item => (
                <div key={item.id} className="command-item" onClick={() => { onSelectItem(item); onClose(false); }}>
                  <i className="bi bi-file-text" /> {item.title}
                </div>
              ))}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
