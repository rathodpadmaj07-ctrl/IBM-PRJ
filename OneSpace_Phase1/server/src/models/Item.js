import mongoose from "mongoose";

export const itemFields = [
  "title", "type", "spaceId", "due", "time", "priority", "completed", "notes", "userId"
];

const itemSchema = new mongoose.Schema({
  title: { type: String, required: true, trim: true },
  type: { type: String, enum: ["task", "idea", "schedule"], default: "task" },
  spaceId: { type: String, default: "" },
  due: { type: String, default: "" },
  time: { type: String, default: "" },
  priority: { type: String, enum: ["low", "medium", "high"], default: "medium" },
  completed: { type: Boolean, default: false },
  notes: { type: String, default: "" },
  userId: { type: String, default: "" }
}, {
  timestamps: true,
  toJSON: {
    transform: (doc, ret) => {
      ret.id = ret._id.toString();
      delete ret._id;
      delete ret.__v;
      return ret;
    }
  }
});

export const Item = mongoose.models.Item || mongoose.model("Item", itemSchema);
