import { Router } from "express";
import {
  clearAllNotifications,
  createNotification,
  deleteNotification,
  listNotifications,
  markAllRead,
  markRead
} from "../controllers/notificationsController.js";

const router = Router();

router.get("/", listNotifications);
router.post("/", createNotification);
router.patch("/read-all", markAllRead);
router.patch("/:id/read", markRead);
router.delete("/clear-all", clearAllNotifications);
router.delete("/:id", deleteNotification);

export default router;
