import React, { useEffect, useMemo, useState } from "react";
import * as api from "./api/client.js";

import { Sidebar } from "./components/Sidebar.jsx";
import { Topbar } from "./components/Topbar.jsx";
import { DashboardView } from "./components/DashboardView.jsx";
import { ItemRow } from "./components/ItemRow.jsx";
import { ItemDrawer } from "./components/ItemDrawer.jsx";
import { CommandMenu } from "./components/CommandMenu.jsx";
import { SettingsView } from "./components/SettingsView.jsx";
import { HelpView } from "./components/HelpView.jsx";
import { NotificationPanel } from "./components/NotificationPanel.jsx";
import { CaptureModal, EditModal, SpaceModal, SpaceEditModal } from "./components/Modals.jsx";

const STORAGE_KEY = "onespace-phase2-data";
const THEME_KEY = "onespace-theme";
const NOTIF_PREFS_KEY = "onespace-notif-prefs";

const defaultSpaces = [
  { id: "personal", name: "Personal", icon: "bi-person" },
  { id: "college", name: "College", icon: "bi-mortarboard" },
  { id: "projects", name: "Projects", icon: "bi-code-slash" }
];

function loadLocalData() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
    if (saved && Array.isArray(saved.items) && Array.isArray(saved.spaces)) return saved;
  } catch {}
  return { items: [], spaces: defaultSpaces };
}

function loadNotifPrefs() {
  try {
    const saved = JSON.parse(localStorage.getItem(NOTIF_PREFS_KEY));
    if (saved) return saved;
  } catch {}
  return { dueSoon: true, dueToday: true, overdue: true, completed: true, timing: "24h" };
}

function normalizeItem(item) {
  return { ...item, id: item.id || item._id, due: item.due ? String(item.due).slice(0, 10) : "" };
}

function normalizeSpace(space) {
  return { ...space, id: space.id || space._id };
}

function today() {
  return new Date().toISOString().slice(0, 10);
}

function todayOffset(offset) {
  const d = new Date();
  d.setDate(d.getDate() + offset);
  return d.toISOString().slice(0, 10);
}

function isOverdue(item) {
  return Boolean(item.due && item.due < today() && !item.completed);
}

function getSpaceName(spaces, id) {
  return spaces.find(space => space.id === id)?.name || "Unsorted";
}

function App() {
  const [data, setData] = useState(loadLocalData);
  const [notifications, setNotifications] = useState([]);
  const [notifPrefs, setNotifPrefs] = useState(loadNotifPrefs);
  const [source, setSource] = useState("local");
  const [active, setActive] = useState("Dashboard");
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [dark, setDark] = useState(() => localStorage.getItem(THEME_KEY) === "dark");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const [captureOpen, setCaptureOpen] = useState(false);
  const [spaceOpen, setSpaceOpen] = useState(false);
  const [commandOpen, setCommandOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);

  const [drawerItem, setDrawerItem] = useState(null);
  const [editing, setEditing] = useState(null);
  const [editingSpace, setEditingSpace] = useState(null);

  useEffect(() => {
    if (source === "local") localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  }, [data, source]);

  useEffect(() => {
    localStorage.setItem(NOTIF_PREFS_KEY, JSON.stringify(notifPrefs));
  }, [notifPrefs]);

  useEffect(() => {
    document.documentElement.setAttribute("data-bs-theme", dark ? "dark" : "light");
    localStorage.setItem(THEME_KEY, dark ? "dark" : "light");
  }, [dark]);

  useEffect(() => {
    if (!notice) return undefined;
    const timer = setTimeout(() => setNotice(""), 2800);
    return () => clearTimeout(timer);
  }, [notice]);

  // Click outside to close notification panel
  useEffect(() => {
    function handleDocClick() {
      if (notifOpen) setNotifOpen(false);
    }
    window.addEventListener("click", handleDocClick);
    return () => window.removeEventListener("click", handleDocClick);
  }, [notifOpen]);

  async function loadFromApi() {
    setLoading(true);
    try {
      const [itemsResponse, spacesResponse, notifResponse] = await Promise.all([
        api.getItems(),
        api.getSpaces(),
        api.getNotifications()
      ]);
      const normalizedItems = (itemsResponse?.data || []).map(normalizeItem);
      setData({
        items: normalizedItems,
        spaces: (spacesResponse?.data || []).map(normalizeSpace)
      });
      if (notifResponse?.data) {
        const completedIds = new Set(normalizedItems.filter(i => i.completed).map(i => i.id));
        const filteredNotifs = notifResponse.data.filter(n => {
          if (n.type === "TASK_COMPLETED") return false;
          if (n.itemId && completedIds.has(n.itemId)) return false;
          return true;
        });
        setNotifications(filteredNotifs);
      }
      setSource("api");
      setError("");
    } catch {
      setError("Unable to connect to OneSpace server. Operating in local mode.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadFromApi();
  }, []);

  // Automatic Deduplicated Task Reminder Evaluator
  useEffect(() => {
    if (!data.items.length) return;

    const newReminders = [];
    const currentDate = today();

    data.items.forEach(item => {
      // Completed tasks suppress overdue reminders
      if (item.completed) return;

      // Overdue Evaluation
      if (notifPrefs.overdue && item.due && item.due < currentDate) {
        const dedupeKey = `${item.id}_OVERDUE_${item.due}`;
        newReminders.push({
          type: "TASK_OVERDUE",
          title: "Task overdue",
          message: `${item.title} was due on ${item.due}.`,
          itemId: item.id,
          spaceId: item.spaceId,
          priority: "high",
          dedupeKey
        });
      }

      // Due Today Evaluation
      if (notifPrefs.dueToday && item.due && item.due === currentDate) {
        const dedupeKey = `${item.id}_TODAY_${currentDate}`;
        newReminders.push({
          type: "TASK_DUE_TODAY",
          title: "Due today",
          message: `${item.title} is due today.`,
          itemId: item.id,
          spaceId: item.spaceId,
          priority: "medium",
          dedupeKey
        });
      }

      // Due Soon Evaluation
      if (notifPrefs.dueSoon && item.due && item.due > currentDate && item.due <= todayOffset(1)) {
        const dedupeKey = `${item.id}_SOON_${item.due}`;
        newReminders.push({
          type: "TASK_DUE_SOON",
          title: "Task due soon",
          message: `${item.title} is due tomorrow (${item.due}).`,
          itemId: item.id,
          spaceId: item.spaceId,
          priority: "low",
          dedupeKey
        });
      }
    });

    if (newReminders.length > 0) {
      newReminders.forEach(async reminder => {
        if (source === "api") {
          try {
            const res = await api.createNotification(reminder);
            if (res?.data) {
              setNotifications(prev => {
                if (prev.some(n => n.dedupeKey === reminder.dedupeKey)) return prev;
                return [res.data, ...prev];
              });
            }
          } catch {}
        } else {
          setNotifications(prev => {
            if (prev.some(n => n.dedupeKey === reminder.dedupeKey)) return prev;
            return [{
              id: crypto.randomUUID(),
              ...reminder,
              read: false,
              createdAt: new Date().toISOString()
            }, ...prev];
          });
        }
      });
    }
  }, [data.items, notifPrefs, source]);

  const spaces = useMemo(() =>
    data.spaces.map(space => ({
      ...space,
      count: data.items.filter(item => item.spaceId === space.id && !item.completed).length
    })),
    [data]
  );

  const stats = {
    total: data.items.length,
    completed: data.items.filter(item => item.completed).length,
    pending: data.items.filter(item => !item.completed).length,
    high: data.items.filter(item => !item.completed && item.priority === "high").length,
    attention: data.items.filter(item => !item.completed && (item.priority === "high" || isOverdue(item))).length
  };

  const visibleItems = useMemo(() => {
    const query = search.trim().toLowerCase();
    let items = data.items.filter(
      item => !query || `${item.title} ${item.notes || ""} ${getSpaceName(spaces, item.spaceId)}`.toLowerCase().includes(query)
    );

    if (active === "Needs Attention") items = items.filter(item => !item.completed && (item.priority === "high" || isOverdue(item)));
    if (active === "Today") items = items.filter(item => !item.completed && item.due === today());
    if (active === "Upcoming") items = items.filter(item => !item.completed && item.due > today());
    if (active === "Ideas") items = items.filter(item => item.type === "idea");
    if (active.startsWith("space:")) items = items.filter(item => item.spaceId === active.slice(6));

    if (filter === "pending") items = items.filter(item => !item.completed);
    if (filter === "completed") items = items.filter(item => item.completed);
    if (filter === "high") items = items.filter(item => item.priority === "high");

    return items.sort((a, b) => (a.due || "9999").localeCompare(b.due || "9999") || (a.time || "").localeCompare(b.time || ""));
  }, [active, data.items, filter, search, spaces]);

  const unreadNotifCount = notifications.filter(n => !n.read).length;

  async function updateItem(id, patch) {
    if (patch.completed) {
      setNotifications(prev => prev.filter(n => n.itemId !== id && !(n.dedupeKey && n.dedupeKey.startsWith(`${id}_`))));
    }

    if (source === "api") {
      setBusy(true);
      try {
        const response = await api.updateItem(id, patch);
        const updated = normalizeItem(response.data);
        setData(current => ({ ...current, items: current.items.map(item => item.id === id ? updated : item) }));
        if (drawerItem?.id === id) setDrawerItem(updated);
        setNotice(patch.completed ? "Nice. One less thing." : "Item updated");
      } catch {
        setError("Unable to update item.");
      } finally {
        setBusy(false);
      }
    } else {
      setData(current => ({
        ...current,
        items: current.items.map(item => item.id === id ? { ...item, ...patch } : item)
      }));
      setNotice(patch.completed ? "Nice. One less thing." : "Item updated");
    }
  }

  async function createItem(item) {
    if (source === "api") {
      setBusy(true);
      try {
        const response = await api.createItem({
          ...item,
          due: item.due || undefined,
          time: item.time || undefined,
          notes: item.notes || undefined
        });
        const created = normalizeItem(response.data);
        setData(current => ({ ...current, items: [created, ...current.items] }));
        setNotice("Item created successfully");

        api.createNotification({
          type: "TASK_CREATED",
          title: "Task created",
          message: `${created.title} was added to ${getSpaceName(spaces, created.spaceId)}.`,
          itemId: created.id,
          priority: "low"
        }).then(res => res?.data && setNotifications(prev => [res.data, ...prev])).catch(() => {});
      } catch {
        setError("Unable to create item.");
      } finally {
        setBusy(false);
      }
    } else {
      const created = { ...item, id: crypto.randomUUID() };
      setData(current => ({
        ...current,
        items: [created, ...current.items]
      }));
      setNotice("Item created successfully");

      setNotifications(prev => [{
        id: crypto.randomUUID(),
        type: "TASK_CREATED",
        title: "Task created",
        message: `${created.title} was added to ${getSpaceName(spaces, created.spaceId)}.`,
        itemId: created.id,
        read: false,
        priority: "low",
        createdAt: new Date().toISOString()
      }, ...prev]);
    }
  }

  async function deleteItem(id) {
    setNotifications(prev => prev.filter(n => n.itemId !== id && !(n.dedupeKey && n.dedupeKey.startsWith(`${id}_`))));
    if (source === "api") {
      setBusy(true);
      try {
        await api.deleteItem(id);
        setData(current => ({ ...current, items: current.items.filter(item => item.id !== id) }));
        setEditing(null);
        if (drawerItem?.id === id) setDrawerItem(null);
        setNotice("Item deleted");
      } catch {
        setError("Unable to delete item.");
      } finally {
        setBusy(false);
      }
    } else {
      setData(current => ({ ...current, items: current.items.filter(item => item.id !== id) }));
      setEditing(null);
      if (drawerItem?.id === id) setDrawerItem(null);
      setNotice("Item deleted");
    }
  }

  async function createSpace(name) {
    if (!name.trim()) return;
    if (source === "api") {
      setBusy(true);
      try {
        const response = await api.createSpace({ name: name.trim(), icon: "bi-folder" });
        const newSpace = normalizeSpace(response.data);
        setData(current => ({ ...current, spaces: [...current.spaces, newSpace] }));
        setNotice("Space created");

        api.createNotification({
          type: "NEW_SPACE",
          title: "New space created",
          message: `${newSpace.name} space has been created.`,
          spaceId: newSpace.id,
          priority: "low"
        }).then(res => res?.data && setNotifications(prev => [res.data, ...prev])).catch(() => {});
      } catch {
        setError("Unable to create Space.");
      } finally {
        setBusy(false);
      }
    } else {
      const newSpace = { id: crypto.randomUUID(), name: name.trim(), icon: "bi-folder" };
      setData(current => ({
        ...current,
        spaces: [...current.spaces, newSpace]
      }));
      setNotice("Space created");

      setNotifications(prev => [{
        id: crypto.randomUUID(),
        type: "NEW_SPACE",
        title: "New space created",
        message: `${newSpace.name} space has been created.`,
        spaceId: newSpace.id,
        read: false,
        priority: "low",
        createdAt: new Date().toISOString()
      }, ...prev]);
    }
    setSpaceOpen(false);
  }

  async function saveSpace(id, name) {
    if (!name.trim()) return;
    if (source === "api") {
      setBusy(true);
      try {
        const response = await api.updateSpace(id, { name: name.trim() });
        setData(current => ({
          ...current,
          spaces: current.spaces.map(space => space.id === id ? normalizeSpace(response.data) : space)
        }));
        setNotice("Space updated");
      } catch {
        setError("Unable to update Space.");
      } finally {
        setBusy(false);
      }
    } else {
      setData(current => ({
        ...current,
        spaces: current.spaces.map(space => space.id === id ? { ...space, name: name.trim() } : space)
      }));
      setNotice("Space updated");
    }
    setEditingSpace(null);
  }

  async function deleteSpace(id) {
    if (source === "api") {
      setBusy(true);
      try {
        await api.deleteSpace(id);
        setData(current => ({
          ...current,
          spaces: current.spaces.filter(space => space.id !== id),
          items: current.items.map(item => item.spaceId === id ? { ...item, spaceId: "" } : item)
        }));
        setNotice("Space deleted");
      } catch {
        setError("Unable to delete Space.");
      } finally {
        setBusy(false);
      }
    } else {
      setData(current => ({ ...current, spaces: current.spaces.filter(space => space.id !== id) }));
      setNotice("Space deleted");
    }
    setEditingSpace(null);
    if (active === `space:${id}`) setActive("Dashboard");
  }

  // Notification Actions
  async function handleMarkNotifRead(id) {
    if (source === "api") {
      try { await api.markNotificationRead(id); } catch {}
    }
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  }

  async function handleMarkAllNotifRead() {
    if (source === "api") {
      try { await api.markAllNotificationsRead(); } catch {}
    }
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  }

  async function handleDeleteNotif(id) {
    if (source === "api") {
      try { await api.deleteNotification(id); } catch {}
    }
    setNotifications(prev => prev.filter(n => n.id !== id));
  }

  async function handleClearAllNotif() {
    if (source === "api") {
      try { await api.clearAllNotifications(); } catch {}
    }
    setNotifications([]);
  }

  function handleSelectTaskItem(itemId) {
    const item = data.items.find(i => i.id === itemId);
    if (item) setDrawerItem(item);
  }

  const pageTitle = active === "Dashboard"
    ? "Dashboard"
    : active.startsWith("space:")
    ? `${getSpaceName(spaces, active.slice(6))} Space`
    : active;

  const contentHeading = active === "Dashboard"
    ? "All Items"
    : active.startsWith("space:")
    ? "Your tasks"
    : active;

  return (
    <div className="app-shell">
      {notice && <div className="toast-message" role="status"><i className="bi bi-check-circle me-2" />{notice}</div>}
      
      <Sidebar
        active={active}
        setActive={setActive}
        spaces={spaces}
        stats={stats}
        onOpenQuickCapture={() => setCaptureOpen(true)}
        onOpenCreateSpace={() => setSpaceOpen(true)}
        onOpenEditSpace={setEditingSpace}
        onDeleteSpace={deleteSpace}
      />

      <main className="main">
        <Topbar
          active={active}
          pageTitle={pageTitle}
          dark={dark}
          setDark={setDark}
          search={search}
          setSearch={setSearch}
          onOpenCommand={setCommandOpen}
          unreadCount={unreadNotifCount}
          onToggleNotifications={e => {
            e.stopPropagation();
            setNotifOpen(!notifOpen);
          }}
          isNotificationOpen={notifOpen}
        />

        {/* Notification Panel Popover */}
        <NotificationPanel
          isOpen={notifOpen}
          onClose={() => setNotifOpen(false)}
          notifications={notifications}
          onMarkRead={handleMarkNotifRead}
          onMarkAllRead={handleMarkAllNotifRead}
          onDeleteNotification={handleDeleteNotif}
          onClearAll={handleClearAllNotif}
          onSelectTaskItem={handleSelectTaskItem}
        />

        <section className="content">
          {active === "Settings" ? (
            <SettingsView
              dark={dark}
              setDark={setDark}
              source={source}
              onReloadApi={loadFromApi}
              notifPrefs={notifPrefs}
              setNotifPrefs={setNotifPrefs}
            />
          ) : active === "Help" ? (
            <HelpView />
          ) : (
            <>
              {active === "Dashboard" && (
                <DashboardView
                  stats={stats}
                  items={data.items}
                  onAdd={() => setCaptureOpen(true)}
                  onOpenItem={setDrawerItem}
                />
              )}

              <div className="list-header">
                <div>
                  <h2>{contentHeading}</h2>
                  <p>{loading ? "Loading items..." : `${visibleItems.length} ${visibleItems.length === 1 ? "item" : "items"}`}</p>
                </div>
                <div className="d-flex align-items-center gap-2">
                  <select
                    className="form-select form-select-sm rounded-pill"
                    value={filter}
                    onChange={e => setFilter(e.target.value)}
                  >
                    <option value="all">All items</option>
                    <option value="pending">Pending</option>
                    <option value="completed">Completed</option>
                    <option value="high">High priority</option>
                  </select>
                  <button className="btn-compact-new" onClick={() => setCaptureOpen(true)}>
                    <i className="bi bi-plus-lg" /> New item
                  </button>
                </div>
              </div>

              <div className="item-list-container">
                {loading ? (
                  <div className="p-5 text-center text-secondary">Loading workspace data...</div>
                ) : visibleItems.length > 0 ? (
                  visibleItems.map(item => (
                    <ItemRow
                      key={item.id}
                      item={item}
                      spaces={spaces}
                      onToggle={() => updateItem(item.id, { completed: !item.completed })}
                      onOpenDrawer={setDrawerItem}
                      onEdit={setEditing}
                      onDelete={() => deleteItem(item.id)}
                    />
                  ))
                ) : (
                  <div className="p-5 text-center text-secondary empty-state-box">
                    <i className="bi bi-inbox fs-3 mb-2 d-block text-muted" />
                    <h4 className="fs-6 fw-bold mb-1 text-primary">No tasks yet</h4>
                    <p className="small mb-3 text-secondary">Add something you want to accomplish.</p>
                    <button className="btn-compact-new mx-auto" onClick={() => setCaptureOpen(true)}>
                      <i className="bi bi-plus-lg me-1" /> New item
                    </button>
                  </div>
                )}
              </div>
            </>
          )}
        </section>
      </main>

      {/* Slide Drawer & Modals */}
      <ItemDrawer
        item={drawerItem}
        spaces={spaces}
        onClose={() => setDrawerItem(null)}
        onToggleComplete={item => updateItem(item.id, { completed: !item.completed })}
        onDelete={deleteItem}
        onEdit={item => { setDrawerItem(null); setEditing(item); }}
      />

      <CommandMenu
        isOpen={commandOpen}
        onClose={setCommandOpen}
        items={data.items}
        spaces={spaces}
        onSelectItem={setDrawerItem}
        onSelectNav={setActive}
        onToggleDark={() => setDark(!dark)}
      />

      {captureOpen && (
        <CaptureModal
          spaces={spaces}
          onClose={() => setCaptureOpen(false)}
          onSave={async item => { await createItem(item); setCaptureOpen(false); }}
          disabled={busy}
        />
      )}

      {spaceOpen && (
        <SpaceModal
          onClose={() => setSpaceOpen(false)}
          onSave={createSpace}
          disabled={busy}
        />
      )}

      {editing && (
        <EditModal
          item={editing}
          spaces={spaces}
          onClose={() => setEditing(null)}
          onSave={async patch => { await updateItem(editing.id, patch); setEditing(null); }}
          onDelete={() => deleteItem(editing.id)}
          disabled={busy}
        />
      )}

      {editingSpace && (
        <SpaceEditModal
          space={editingSpace}
          onClose={() => setEditingSpace(null)}
          onSave={saveSpace}
          onDelete={deleteSpace}
          disabled={busy}
        />
      )}
    </div>
  );
}

export default App;
