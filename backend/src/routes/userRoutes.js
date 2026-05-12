const express = require("express");
const router = express.Router();
const { updateProfile } = require("../controllers/userController");
const { authenticate } = require("../middleware/authMiddleware");

router.put("/profile", authenticate, updateProfile); // Gunakan PUT sesuai rencana awal

module.exports = router;
