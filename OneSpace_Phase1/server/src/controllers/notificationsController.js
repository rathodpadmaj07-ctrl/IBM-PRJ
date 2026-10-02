import { createId, notifications, items as inMemoryItems } from "../data/store.js";
import { isConnected } from "../config/database.js";
import { Item } from "../models/Item.js";

export async function listNotifications(req, res) {
  // Purge any completed task notifications or TASK_COMPLETED notifications
  if (isConnected()) {
    try {
      const completedDocs = await Item.find({ completed: true }, "_id");
      const completedIds = new Set(completedDocs.map(d => d._id.toString()));
      for (let i = notifications.length - 1; i >= 0; i--) {
        const n = notifications[i];
        if (n.type === "TASK_COMPLETED" || (n.itemId && completedIds.has(n.itemId.toString()))) {
          notifications.splice(i, 1);
        }
      }
    } catch (err) {
      console.error("DB Error listNotifications purge:", err);
    }
  } else {
    const completedIds = new Set(inMemoryItems.filter(i => i.completed).map(i => i.id));
    for (let i = notifications.length - 1; i >= 0; i--) {
      const n = notifications[i];
      if (n.type === "TASK_COMPLETED" || (n.itemId && completedIds.has(n.itemId))) {
        notifications.splice(i, 1);
      }
    }
  }

  const data = [...notifications].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  return res.status(200).json({ success: true, data });
}

export async function createNotification(req, res) {
  const { type, title, message, itemId, spaceId, priority, dedupeKey } = req.body;
  if (!title) return res.status(400).json({ success: false, message: "title is required" });

  // Suppress task completed confirmation notifications
  if (type === "TASK_COMPLETED") {
    return res.status(200).json({ success: true, message: "Task completed notification suppressed", data: null });
  }

  // Check if item is already completed
  if (itemId) {
    let isCompleted = false;
    if (isConnected()) {
      try {
        const doc = await Item.findById(itemId);
        if (doc && doc.completed) isCompleted = true;
      } catch (err) {}
    } else {
      const item = inMemoryItems.find(i => i.id === itemId);
      if (item && item.completed) isCompleted = true;
    }
    if (isCompleted) {
      return res.status(200).json({ success: true, message: "Item is completed; notification suppressed", data: null });
    }
  }

  // Deterministic deduplication check
  if (dedupeKey) {
    const exists = notifications.some(n => n.dedupeKey === dedupeKey);
    if (exists) {
      return res.status(200).json({ success: true, message: "Notification already exists", data: null });
    }
  }

  const now = new Date().toISOString();
  const notification = {
    id: createId(),
    type: type || "TASK_DUE_SOON",
    title: title.trim(),
    message: message ? message.trim() : "",
    itemId: itemId || "",
    spaceId: spaceId || "",
    priority: priority || "low",
    dedupeKey: dedupeKey || "",
    read: false,
    createdAt: now
  };

  notifications.unshift(notification);
  return res.status(201).json({ success: true, data: notification });
}

export async function markRead(req, res) {
  const { id } = req.params;
  const item = notifications.find(n => n.id === id);
  if (!item) return res.status(404).json({ success: false, message: "Notification not found" });
  item.read = true;
  return res.status(200).json({ success: true, data: item });
}

export async function markAllRead(req, res) {
  notifications.forEach(n => { n.read = true; });
  return res.status(200).json({ success: true, message: "All notifications marked as read" });
}

export async function deleteNotification(req, res) {
  const { id } = req.params;
  const index = notifications.findIndex(n => n.id === id);
  if (index < 0) return res.status(404).json({ success: false, message: "Notification not found" });
  notifications.splice(index, 1);
  return res.status(204).send();
}

export async function clearAllNotifications(req, res) {
  notifications.length = 0;
  return res.status(204).send();
}
