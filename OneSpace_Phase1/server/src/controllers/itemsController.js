import { createId, items as inMemoryItems, notifications } from "../data/store.js";
import { isConnected } from "../config/database.js";
import { Item } from "../models/Item.js";

const allowedTypes = new Set(["task", "idea", "schedule"]);
const allowedPriorities = new Set(["low", "medium", "high"]);
const fields = new Set(["title", "type", "spaceId", "due", "time", "priority", "completed", "notes", "userId"]);

function validateItem(body, partial = false) {
  if (!partial && (typeof body.title !== "string" || !body.title.trim())) return "title is required";
  if (body.title !== undefined && (typeof body.title !== "string" || !body.title.trim())) return "title must be a non-empty string";
  if (body.type !== undefined && !allowedTypes.has(body.type)) return "type must be task, idea, or schedule";
  if (body.priority !== undefined && !allowedPriorities.has(body.priority)) return "priority must be low, medium, or high";
  if (body.completed !== undefined && typeof body.completed !== "boolean") return "completed must be a boolean";
  if (body.due !== undefined && body.due !== "" && Number.isNaN(Date.parse(body.due))) return "due must be a valid date";
  return null;
}

function pickFields(body) { return Object.fromEntries(Object.entries(body).filter(([key]) => fields.has(key))); }

export async function listItems(req, res) {
  if (isConnected()) {
    try {
      const items = await Item.find().sort({ due: 1, time: 1 });
      return res.status(200).json({ success: true, data: items.map(doc => doc.toJSON()) });
    } catch (err) {
      console.error("DB Error listItems:", err);
    }
  }
  const data = [...inMemoryItems].sort((a, b) => (a.due || "9999").localeCompare(b.due || "9999") || (a.time || "").localeCompare(b.time || ""));
  return res.status(200).json({ success: true, data });
}

export async function createItem(req, res) {
  const message = validateItem(req.body);
  if (message) return res.status(400).json({ success: false, message });
  
  const payload = {
    ...pickFields(req.body),
    title: req.body.title.trim(),
    priority: req.body.priority || "medium",
    completed: req.body.completed || false
  };

  if (isConnected()) {
    try {
      const doc = await Item.create(payload);
      return res.status(201).json({ success: true, data: doc.toJSON() });
    } catch (err) {
      console.error("DB Error createItem:", err);
    }
  }

  const now = new Date().toISOString();
  const item = { id: createId(), ...payload, createdAt: now, updatedAt: now };
  inMemoryItems.push(item);
  return res.status(201).json({ success: true, data: item });
}

export async function updateItem(req, res) {
  const message = validateItem(req.body, true);
  if (message) return res.status(400).json({ success: false, message });

  const payload = pickFields(req.body);
  if (req.body.title) payload.title = req.body.title.trim();

  // Clean up active notifications if task is completed
  if (payload.completed === true) {
    for (let i = notifications.length - 1; i >= 0; i--) {
      if (notifications[i].itemId === req.params.id || (notifications[i].dedupeKey && notifications[i].dedupeKey.startsWith(`${req.params.id}_`))) {
        notifications.splice(i, 1);
      }
    }
  }

  if (isConnected()) {
    try {
      const doc = await Item.findByIdAndUpdate(req.params.id, payload, { new: true });
      if (!doc) return res.status(404).json({ success: false, message: "Item not found" });
      return res.status(200).json({ success: true, data: doc.toJSON() });
    } catch (err) {
      console.error("DB Error updateItem:", err);
    }
  }

  const index = inMemoryItems.findIndex(item => item.id === req.params.id);
  if (index < 0) return res.status(404).json({ success: false, message: "Item not found" });
  inMemoryItems[index] = { ...inMemoryItems[index], ...payload, updatedAt: new Date().toISOString() };
  return res.status(200).json({ success: true, data: inMemoryItems[index] });
}

export async function deleteItem(req, res) {
  // Also clean up notifications when task is deleted
  for (let i = notifications.length - 1; i >= 0; i--) {
    if (notifications[i].itemId === req.params.id || (notifications[i].dedupeKey && notifications[i].dedupeKey.startsWith(`${req.params.id}_`))) {
      notifications.splice(i, 1);
    }
  }

  if (isConnected()) {
    try {
      const doc = await Item.findByIdAndDelete(req.params.id);
      if (!doc) return res.status(404).json({ success: false, message: "Item not found" });
      return res.status(204).send();
    } catch (err) {
      console.error("DB Error deleteItem:", err);
    }
  }

  const index = inMemoryItems.findIndex(item => item.id === req.params.id);
  if (index < 0) return res.status(404).json({ success: false, message: "Item not found" });
  inMemoryItems.splice(index, 1);
  return res.status(204).send();
}
