const express = require("express");
const router = express.Router();
const { getProfile, updateProfile } = require("../controllers/userController");
const { authenticate } = require("../middleware/authMiddleware");

router.put("/profile", authenticate, updateProfile); // pake PUT sesuai rencana awal
router.get("/profile", authenticate, getProfile);

module.exports = router;
