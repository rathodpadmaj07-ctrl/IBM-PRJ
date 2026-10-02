import { Router } from "express";
import { createSpace, deleteSpace, listSpaces, updateSpace } from "../controllers/spacesController.js";

const router = Router();
router.get("/", listSpaces);
router.post("/", createSpace);
router.patch("/:id", updateSpace);
router.delete("/:id", deleteSpace);

export default router;
