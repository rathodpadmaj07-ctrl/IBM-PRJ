import { createId, items as inMemoryItems, spaces as inMemorySpaces } from "../data/store.js";
import { isConnected } from "../config/database.js";
import { Space } from "../models/Space.js";
import { Item } from "../models/Item.js";

function validateSpace(body, partial = false) {
  if (!partial && (typeof body.name !== "string" || !body.name.trim())) return "name is required";
  if (body.name !== undefined && (typeof body.name !== "string" || !body.name.trim())) return "name must be a non-empty string";
  if (body.icon !== undefined && typeof body.icon !== "string") return "icon must be a string";
  return null;
}

export async function listSpaces(req, res) {
  if (isConnected()) {
    try {
      const spaces = await Space.find().sort({ createdAt: 1 });
      return res.status(200).json({ success: true, data: spaces.map(doc => doc.toJSON()) });
    } catch (err) {
      console.error("DB Error listSpaces:", err);
    }
  }
  return res.status(200).json({ success: true, data: [...inMemorySpaces] });
}

export async function createSpace(req, res) {
  const message = validateSpace(req.body);
  if (message) return res.status(400).json({ success: false, message });
  
  const payload = {
    name: req.body.name.trim(),
    icon: req.body.icon || "bi-folder"
  };

  if (isConnected()) {
    try {
      const doc = await Space.create(payload);
      return res.status(201).json({ success: true, data: doc.toJSON() });
    } catch (err) {
      console.error("DB Error createSpace:", err);
    }
  }

  const now = new Date().toISOString();
  const space = { id: createId(), ...payload, createdAt: now, updatedAt: now };
  inMemorySpaces.push(space);
  return res.status(201).json({ success: true, data: space });
}

export async function updateSpace(req, res) {
  const message = validateSpace(req.body, true);
  if (message) return res.status(400).json({ success: false, message });

  const payload = {};
  if (req.body.name) payload.name = req.body.name.trim();
  if (req.body.icon !== undefined) payload.icon = req.body.icon;

  if (isConnected()) {
    try {
      const doc = await Space.findByIdAndUpdate(req.params.id, payload, { new: true });
      if (!doc) return res.status(404).json({ success: false, message: "Space not found" });
      return res.status(200).json({ success: true, data: doc.toJSON() });
    } catch (err) {
      console.error("DB Error updateSpace:", err);
    }
  }

  const index = inMemorySpaces.findIndex(space => space.id === req.params.id);
  if (index < 0) return res.status(404).json({ success: false, message: "Space not found" });
  inMemorySpaces[index] = { ...inMemorySpaces[index], ...payload, updatedAt: new Date().toISOString() };
  return res.status(200).json({ success: true, data: inMemorySpaces[index] });
}

export async function deleteSpace(req, res) {
  if (isConnected()) {
    try {
      const doc = await Space.findByIdAndDelete(req.params.id);
      if (!doc) return res.status(404).json({ success: false, message: "Space not found" });
      await Item.updateMany({ spaceId: req.params.id }, { spaceId: "" });
      return res.status(204).send();
    } catch (err) {
      console.error("DB Error deleteSpace:", err);
    }
  }

  const index = inMemorySpaces.findIndex(space => space.id === req.params.id);
  if (index < 0) return res.status(404).json({ success: false, message: "Space not found" });
  const [removed] = inMemorySpaces.splice(index, 1);
  for (let i = 0; i < inMemoryItems.length; i++) {
    if (inMemoryItems[i].spaceId === removed.id) {
      inMemoryItems[i].spaceId = "";
    }
  }
  return res.status(204).send();
}
