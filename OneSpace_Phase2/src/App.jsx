import React, { useEffect, useMemo, useState } from "react";

const STORAGE_KEY = "onespace-phase2-data";
const THEME_KEY = "onespace-theme";

const defaultSpaces = [
  { id: "personal", name: "Personal", icon: "bi-person", count: 0 },
  { id: "college", name: "College", icon: "bi-mortarboard", count: 0 },
  { id: "projects", name: "Projects", icon: "bi-code-slash", count: 0 }
];

const seedItems = [
  { id: "seed1", title: "Finish your FSD assignment", type: "task", spaceId: "college", due: todayOffset(1), priority: "high", completed: false, createdAt: Date.now() - 3600000, notes: "Complete the remaining assessment work." },
  { id: "seed2", title: "Pattern Recognition practical", type: "schedule", spaceId: "college", due: todayOffset(0), time: "10:00", priority: "medium", completed: false, createdAt: Date.now() - 7200000 },
  { id: "seed3", title: "Work on OneSpace", type: "task", spaceId: "projects", due: todayOffset(0), time: "14:30", priority: "medium", completed: false, createdAt: Date.now() - 1800000 },
  { id: "seed4", title: "Build a small Unreal Engine prototype", type: "idea", spaceId: "projects", due: "", priority: "low", completed: false, createdAt: Date.now() - 7200000 },
  { id: "seed5", title: "Guitar practice", type: "schedule", spaceId: "personal", due: todayOffset(0), time: "18:00", priority: "low", completed: false, createdAt: Date.now() - 5000000 },
  { id: "seed6", title: "Semester planning", type: "task", spaceId: "personal", due: todayOffset(7), priority: "low", completed: false, createdAt: Date.now() - 4000000 }
];

function todayOffset(offset) {
  const d = new Date();
  d.setHours(12,0,0,0);
  d.setDate(d.getDate() + offset);
  return d.toISOString().slice(0,10);
}

function loadData() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {}
  return { items: seedItems, spaces: defaultSpaces };
}

function formatDate(date) {
  if (!date) return "No due date";
  const d = new Date(date + "T12:00:00");
  return d.toLocaleDateString("en-IN", { day:"numeric", month:"short" });
}

function isToday(date) {
  return date === todayOffset(0);
}

function isOverdue(date, completed=false) {
  return Boolean(date && date < todayOffset(0) && !completed);
}

function getSpaceName(spaces, id) {
  return spaces.find(s => s.id === id)?.name || "Unsorted";
}

function App() {
  const [data, setData] = useState(loadData);
  const [active, setActive] = useState("Dashboard");
  const [dark, setDark] = useState(() => localStorage.getItem(THEME_KEY) === "dark");
  const [showCapture, setShowCapture] = useState(false);
  const [showSpace, setShowSpace] = useState(false);
  const [editing, setEditing] = useState(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  }, [data]);

  useEffect(() => {
    document.documentElement.setAttribute("data-bs-theme", dark ? "dark" : "light");
    localStorage.setItem(THEME_KEY, dark ? "dark" : "light");
  }, [dark]);

  const spaces = useMemo(() =>
    data.spaces.map(s => ({...s, count:data.items.filter(i => i.spaceId === s.id && !i.completed).length})),
    [data]
  );

  const visibleItems = useMemo(() => {
    let list = [...data.items];
    const q = search.trim().toLowerCase();
    if (q) list = list.filter(i => `${i.title} ${i.notes || ""} ${getSpaceName(spaces,i.spaceId)}`.toLowerCase().includes(q));

    if (active === "Needs Attention") {
      list = list.filter(i => !i.completed && (i.priority === "high" || isOverdue(i.due)));
    } else if (active === "Today") {
      list = list.filter(i => !i.completed && isToday(i.due));
    } else if (active === "Upcoming") {
      list = list.filter(i => !i.completed && i.due && i.due > todayOffset(0));
    } else if (active === "Ideas") {
      list = list.filter(i => i.type === "idea");
    } else if (active.startsWith("space:")) {
      const id = active.slice(6);
      list = list.filter(i => i.spaceId === id);
    } else if (active !== "Dashboard") {
      list = list.filter(i => !i.completed);
    }
    return list.sort((a,b) => {
      const da = a.due || "9999-12-31", db = b.due || "9999-12-31";
      return da.localeCompare(db) || (a.time || "").localeCompare(b.time || "");
    });
  }, [data.items, active, search, spaces]);

  const stats = {
    attention: data.items.filter(i => !i.completed && (i.priority === "high" || isOverdue(i.due))).length,
    today: data.items.filter(i => !i.completed && isToday(i.due)).length,
    upcoming: data.items.filter(i => !i.completed && i.due > todayOffset(0)).length,
    ideas: data.items.filter(i => i.type === "idea").length
  };

  function updateItem(id, patch) {
    setData(d => ({...d, items:d.items.map(i => i.id === id ? {...i,...patch} : i)}));
  }

  function deleteItem(id) {
    setData(d => ({...d, items:d.items.filter(i => i.id !== id)}));
    if (editing?.id === id) setEditing(null);
  }

  function addItem(item) {
    setData(d => ({...d, items:[{...item,id:crypto.randomUUID(),createdAt:Date.now()},...d.items]}));
  }

  function addSpace(name) {
    const clean = name.trim();
    if (!clean) return;
    const id = crypto.randomUUID();
    setData(d => ({...d, spaces:[...d.spaces,{id,name:clean,icon:"bi-folder",count:0}]}));
    setShowSpace(false);
  }

  function renameSpace(id, name) {
    const clean = name.trim();
    if (!clean) return;
    setData(d => ({...d, spaces:d.spaces.map(s => s.id===id ? {...s,name:clean}:s)}));
  }

  function deleteSpace(id) {
    if (data.spaces.length <= 1) return;
    setData(d => ({
      spaces:d.spaces.filter(s=>s.id!==id),
      items:d.items.map(i=>i.spaceId===id ? {...i,spaceId:""}:i)
    }));
    if (active === `space:${id}`) setActive("Dashboard");
  }

  function resetDemo() {
    if (confirm("Reset OneSpace to the demo data? Your current local data will be replaced.")) {
      setData({items:seedItems,spaces:defaultSpaces});
      setActive("Dashboard");
    }
  }

  const pageTitle = active === "Dashboard" ? "Dashboard" :
    active.startsWith("space:") ? getSpaceName(spaces, active.slice(6)) : active;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><i className="bi bi-layers-fill"/></div>
          <span>OneSpace</span>
        </div>

        <button className="quick-capture" onClick={() => setShowCapture(true)}>
          <i className="bi bi-plus-lg"/> Quick Capture
        </button>

        <div className="nav-section">
          <div className="nav-label">WORKSPACE</div>
          {[
            ["Dashboard","bi-grid-1x2-fill"],
            ["Needs Attention","bi-exclamation-circle"],
            ["Today","bi-calendar3"],
            ["Upcoming","bi-calendar-week"],
            ["Ideas","bi-lightbulb"]
          ].map(([label,icon]) =>
            <button key={label} className={`side-link ${active===label ? "active":""}`} onClick={()=>setActive(label)}>
              <i className={`bi ${icon}`}/><span>{label}</span>
              {label==="Needs Attention" && stats.attention>0 && <small>{stats.attention}</small>}
            </button>
          )}
        </div>

        <div className="nav-section spaces-section">
          <div className="space-heading">
            <span className="nav-label mb-0">SPACES</span>
            <button className="icon-btn" title="Create space" onClick={()=>setShowSpace(true)}><i className="bi bi-plus"/></button>
          </div>
          {spaces.map(s =>
            <button key={s.id} className={`side-link ${active===`space:${s.id}`?"active":""}`} onClick={()=>setActive(`space:${s.id}`)}>
              <i className={`bi ${s.icon}`}/><span>{s.name}</span><small>{s.count}</small>
            </button>
          )}
        </div>

        <div className="sidebar-bottom">
          <button className="side-link" onClick={()=>setActive("Settings")}><i className="bi bi-gear"/><span>Settings</span></button>
          <button className="side-link" onClick={()=>setActive("Help")}><i className="bi bi-question-circle"/><span>Help</span></button>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <div className="eyebrow">{new Date().toLocaleDateString("en-IN",{weekday:"long",month:"long",day:"numeric"}).toUpperCase()}</div>
            <h1>{pageTitle}</h1>
          </div>
          <div className="top-actions">
            <div className="search-box">
              <i className="bi bi-search"/>
              <input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search..." />
              {search && <button onClick={()=>setSearch("")}><i className="bi bi-x"/></button>}
            </div>
            <button className="icon-btn" onClick={()=>setDark(!dark)} title="Toggle theme"><i className={`bi ${dark?"bi-sun":"bi-moon"}`}/></button>
            <div className="avatar">PR</div>
          </div>
        </header>

        <section className="content">
          {active === "Settings" ? (
            <Settings dark={dark} setDark={setDark} resetDemo={resetDemo}/>
          ) : active === "Help" ? (
            <Help/>
          ) : (
            <>
              {active==="Dashboard" && <Dashboard stats={stats} items={data.items} spaces={spaces} onAdd={()=>setShowCapture(true)} onOpen={setEditing}/>}
              <div className="list-header">
                <div>
                  <h2>{active==="Dashboard" ? "All items" : active.startsWith("space:") ? getSpaceName(spaces,active.slice(6)) : active}</h2>
                  <p>{visibleItems.length} {visibleItems.length===1?"item":"items"}</p>
                </div>
                <button className="btn btn-dark rounded-pill px-3" onClick={()=>setShowCapture(true)}><i className="bi bi-plus-lg me-2"/>Add</button>
              </div>

              {visibleItems.length === 0 ? (
                <EmptyState active={active} onAdd={()=>setShowCapture(true)}/>
              ) : (
                <div className="item-list">
                  {visibleItems.map(item =>
                    <ItemRow key={item.id} item={item} spaces={spaces}
                      onToggle={()=>updateItem(item.id,{completed:!item.completed})}
                      onEdit={()=>setEditing(item)}
                      onDelete={()=>deleteItem(item.id)}/>
                  )}
                </div>
              )}
            </>
          )}
        </section>
      </main>

      {showCapture && <CaptureModal spaces={spaces} onClose={()=>setShowCapture(false)} onSave={item=>{addItem(item);setShowCapture(false)}}/>}
      {showSpace && <SpaceModal onClose={()=>setShowSpace(false)} onSave={addSpace}/>}
      {editing && <EditModal item={editing} spaces={spaces} onClose={()=>setEditing(null)} onSave={patch=>{updateItem(editing.id,patch);setEditing(null)}} onDelete={()=>deleteItem(editing.id)}/>}
    </div>
  );
}

function Dashboard({stats,items,onAdd,onOpen}) {
  const attention = items.filter(i=>!i.completed && (i.priority==="high" || isOverdue(i.due))).sort((a,b)=>(a.due||"").localeCompare(b.due||""))[0];
  return <div className="dashboard-block">
    <div className="hero-row">
      <div><h2>Everything in one place.</h2><p>Keep track of what matters, what needs attention, and what's coming next.</p></div>
      <button className="btn btn-dark rounded-pill px-4" onClick={onAdd}><i className="bi bi-plus-lg me-2"/>Add something</button>
    </div>
    <div className="stat-grid">
      <Stat icon="bi-exclamation-circle" label="Needs attention" value={stats.attention}/>
      <Stat icon="bi-calendar3" label="Today" value={stats.today}/>
      <Stat icon="bi-calendar-week" label="Upcoming" value={stats.upcoming}/>
      <Stat icon="bi-lightbulb" label="Ideas" value={stats.ideas}/>
    </div>
    {attention ? <div className="attention-card">
      <div className="attention-icon"><i className="bi bi-exclamation-lg"/></div>
      <div className="flex-grow-1"><div className="card-kicker">NEEDS ATTENTION</div><h3>{attention.title}</h3><p>{isOverdue(attention.due) ? `Overdue · ${formatDate(attention.due)}` : `Due ${formatDate(attention.due)}`}</p></div>
      <button className="btn btn-outline-secondary rounded-pill" onClick={()=>onOpen(attention)}>Open</button>
    </div> : <div className="success-card"><i className="bi bi-check-circle"/> Nothing needs immediate attention. Nice.</div>}
  </div>
}

function Stat({icon,label,value}) {
  return <div className="stat-card"><div className="stat-icon"><i className={`bi ${icon}`}/></div><div><b>{value}</b><span>{label}</span></div></div>
}

function ItemRow({item,spaces,onToggle,onEdit,onDelete}) {
  return <div className={`item-row ${item.completed?"completed":""}`}>
    <button className={`check-button ${item.completed?"checked":""}`} onClick={onToggle}>{item.completed && <i className="bi bi-check2"/>}</button>
    <div className="item-main" onClick={onEdit}>
      <div className="item-title">{item.title}</div>
      <div className="item-meta">
        <span className={`type-pill type-${item.type}`}>{item.type}</span>
        <span><i className="bi bi-folder2-open"/> {getSpaceName(spaces,item.spaceId)}</span>
        {item.due && <span className={isOverdue(item.due,item.completed)?"overdue":""}><i className="bi bi-calendar3"/> {isToday(item.due)?"Today":formatDate(item.due)}</span>}
        {item.time && <span><i className="bi bi-clock"/> {item.time}</span>}
        <span className={`priority ${item.priority}`}>{item.priority}</span>
      </div>
    </div>
    <div className="item-actions">
      <button className="icon-btn" title="Edit" onClick={onEdit}><i className="bi bi-pencil"/></button>
      <button className="icon-btn danger-hover" title="Delete" onClick={onDelete}><i className="bi bi-trash3"/></button>
    </div>
  </div>
}

function EmptyState({active,onAdd}) {
  const text = active==="Ideas" ? "No ideas yet." : active==="Today" ? "Your day is clear." : active==="Upcoming" ? "Nothing upcoming." : active==="Needs Attention" ? "You're all caught up." : "Nothing here yet.";
  return <div className="empty-state"><div className="empty-icon"><i className="bi bi-inbox"/></div><h3>{text}</h3><p>Add something with Quick Capture to get started.</p><button className="btn btn-dark rounded-pill" onClick={onAdd}><i className="bi bi-plus-lg me-2"/>Add something</button></div>
}

function CaptureModal({spaces,onClose,onSave}) {
  const [form,setForm]=useState({title:"",type:"task",spaceId:spaces[0]?.id||"",due:todayOffset(0),time:"",priority:"medium",notes:""});
  const set=(k,v)=>setForm(f=>({...f,[k]:v}));
  function submit(e){e.preventDefault();if(!form.title.trim())return;onSave({...form,title:form.title.trim()})}
  return <Modal title="Quick Capture" onClose={onClose}>
    <form onSubmit={submit}>
      <label className="form-label">What do you want to capture?</label>
      <input className="form-control form-control-lg mb-3" autoFocus value={form.title} onChange={e=>set("title",e.target.value)} placeholder="e.g. Finish project documentation"/>
      <div className="form-grid">
        <Field label="Type"><select className="form-select" value={form.type} onChange={e=>set("type",e.target.value)}><option value="task">Task</option><option value="idea">Idea</option><option value="schedule">Schedule</option></select></Field>
        <Field label="Space"><select className="form-select" value={form.spaceId} onChange={e=>set("spaceId",e.target.value)}>{spaces.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}</select></Field>
        <Field label="Due date"><input type="date" className="form-control" value={form.due} onChange={e=>set("due",e.target.value)}/></Field>
        <Field label="Time (optional)"><input type="time" className="form-control" value={form.time} onChange={e=>set("time",e.target.value)}/></Field>
        <Field label="Priority"><select className="form-select" value={form.priority} onChange={e=>set("priority",e.target.value)}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option></select></Field>
      </div>
      <Field label="Notes"><textarea className="form-control" rows="3" value={form.notes} onChange={e=>set("notes",e.target.value)} placeholder="Optional notes"/></Field>
      <ModalButtons onClose={onClose} submit="Capture"/>
    </form>
  </Modal>
}

function EditModal({item,spaces,onClose,onSave,onDelete}) {
  const [form,setForm]=useState({...item});
  const set=(k,v)=>setForm(f=>({...f,[k]:v}));
  function submit(e){e.preventDefault();onSave({...form,title:form.title.trim()})}
  return <Modal title="Edit item" onClose={onClose}>
    <form onSubmit={submit}>
      <label className="form-label">Title</label><input className="form-control mb-3" autoFocus value={form.title} onChange={e=>set("title",e.target.value)}/>
      <div className="form-grid">
        <Field label="Type"><select className="form-select" value={form.type} onChange={e=>set("type",e.target.value)}><option value="task">Task</option><option value="idea">Idea</option><option value="schedule">Schedule</option></select></Field>
        <Field label="Space"><select className="form-select" value={form.spaceId} onChange={e=>set("spaceId",e.target.value)}>{spaces.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}</select></Field>
        <Field label="Due date"><input type="date" className="form-control" value={form.due||""} onChange={e=>set("due",e.target.value)}/></Field>
        <Field label="Time"><input type="time" className="form-control" value={form.time||""} onChange={e=>set("time",e.target.value)}/></Field>
        <Field label="Priority"><select className="form-select" value={form.priority} onChange={e=>set("priority",e.target.value)}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option></select></Field>
      </div>
      <Field label="Notes"><textarea className="form-control" rows="3" value={form.notes||""} onChange={e=>set("notes",e.target.value)}/></Field>
      <div className="d-flex justify-content-between align-items-center mt-4">
        <button type="button" className="btn btn-outline-danger rounded-pill" onClick={onDelete}><i className="bi bi-trash3 me-2"/>Delete</button>
        <div className="d-flex gap-2"><button type="button" className="btn btn-light" onClick={onClose}>Cancel</button><button className="btn btn-dark">Save changes</button></div>
      </div>
    </form>
  </Modal>
}

function SpaceModal({onClose,onSave}) {
  const [name,setName]=useState("");
  return <Modal title="Create Space" onClose={onClose}><form onSubmit={e=>{e.preventDefault();onSave(name)}}><label className="form-label">Space name</label><input className="form-control mb-3" autoFocus value={name} onChange={e=>setName(e.target.value)} placeholder="e.g. Career"/><ModalButtons onClose={onClose} submit="Create"/></form></Modal>
}

function Modal({title,onClose,children}) {
  return <div className="modal-backdrop-custom" onMouseDown={e=>e.target===e.currentTarget&&onClose()}><div className="modal-card"><div className="modal-head"><h3>{title}</h3><button className="icon-btn" onClick={onClose}><i className="bi bi-x-lg"/></button></div>{children}</div></div>
}

function ModalButtons({onClose,submit}) {
  return <div className="d-flex justify-content-end gap-2 mt-4"><button type="button" className="btn btn-light" onClick={onClose}>Cancel</button><button className="btn btn-dark">{submit}</button></div>
}

function Field({label,children}) { return <div className="field"><label className="form-label">{label}</label>{children}</div> }

function Settings({dark,setDark,resetDemo}) {
  return <div className="settings-page"><div className="settings-intro"><div className="eyebrow">PREFERENCES</div><h2>Settings</h2><p>Customize how OneSpace looks and behaves.</p></div><div className="settings-card"><div><b>Appearance</b><p>Switch between light and dark mode.</p></div><button className="btn btn-outline-secondary rounded-pill" onClick={()=>setDark(!dark)}><i className={`bi ${dark?"bi-sun":"bi-moon"} me-2`}/>{dark?"Light mode":"Dark mode"}</button></div><div className="settings-card"><div><b>Demo data</b><p>Restore the original Phase 2 sample data.</p></div><button className="btn btn-outline-danger rounded-pill" onClick={resetDemo}>Reset demo</button></div></div>
}

function Help() {
  return <div className="help-page"><div className="eyebrow">GET STARTED</div><h2>How OneSpace works</h2><p className="lead">Capture anything, organize it into Spaces, and let the dashboard surface what matters.</p><div className="help-grid"><HelpCard icon="bi-plus-circle" title="Quick Capture" text="Add tasks, ideas, and scheduled items with a due date, priority, and Space."/><HelpCard icon="bi-check2-circle" title="Complete items" text="Click the circle beside an item to mark it complete. Completed items stay saved locally."/><HelpCard icon="bi-search" title="Search" text="Use the search box in the top bar to find items across your Spaces."/><HelpCard icon="bi-folder2-open" title="Spaces" text="Create Spaces for areas like College, Projects, Career, or Personal."/><HelpCard icon="bi-cloud-slash" title="Local first" text="Phase 2 stores your data in this browser using localStorage. Backend sync comes later."/><HelpCard icon="bi-moon" title="Theme" text="Your light/dark preference is remembered automatically." /></div></div>
}

function HelpCard({icon,title,text}) { return <div className="help-card"><div className="help-icon"><i className={`bi ${icon}`}/></div><h3>{title}</h3><p>{text}</p></div> }

export default App;
