import mongoose from "mongoose";

const spaceSchema = new mongoose.Schema({
  name: { type: String, required: true, trim: true },
  icon: { type: String, default: "bi-folder" }
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

export const Space = mongoose.models.Space || mongoose.model("Space", spaceSchema);
