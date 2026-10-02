import { randomUUID } from "node:crypto";

export const spaces = [
  { id: "personal", name: "Personal", icon: "bi-person", createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() },
  { id: "college", name: "College", icon: "bi-mortarboard", createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() },
  { id: "projects", name: "Projects", icon: "bi-code-slash", createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() }
];

function todayOffset(offset) {
  const d = new Date();
  d.setHours(12, 0, 0, 0);
  d.setDate(d.getDate() + offset);
  return d.toISOString().slice(0, 10);
}

export const items = [
  { id: "seed1", title: "Finish your FSD assignment", type: "task", spaceId: "college", due: todayOffset(1), priority: "high", completed: false, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString(), notes: "Complete the remaining assessment work." },
  { id: "seed2", title: "Pattern Recognition practical", type: "schedule", spaceId: "college", due: todayOffset(0), time: "10:00", priority: "medium", completed: false, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() },
  { id: "seed3", title: "Work on OneSpace", type: "task", spaceId: "projects", due: todayOffset(0), time: "14:30", priority: "medium", completed: false, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() },
  { id: "seed4", title: "Build a small prototype", type: "idea", spaceId: "projects", due: "", priority: "low", completed: false, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() },
  { id: "seed5", title: "Guitar practice", type: "schedule", spaceId: "personal", due: todayOffset(0), time: "18:00", priority: "low", completed: false, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() },
  { id: "seed6", title: "Semester planning", type: "task", spaceId: "personal", due: todayOffset(7), priority: "low", completed: false, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() }
];

export const notifications = [];
export const users = [];

export function createId() {
  return randomUUID();
}
