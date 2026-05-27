const express = require("express");
const router = express.Router();
const {
  getProfile,
  updateProfile,
  deleteAccount,
} = require("../controllers/userController");
const { authenticate } = require("../middleware/authMiddleware");

router.put("/profile", authenticate, updateProfile);
router.get("/profile", authenticate, getProfile);
router.delete("/account", authenticate, deleteAccount);

module.exports = router;
