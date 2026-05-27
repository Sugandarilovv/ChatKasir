const express = require("express");
const router = express.Router();
const { authenticate } = require("../middleware/authMiddleware");
const { getMonthlyReport } = require("../controllers/reportController");

router.get("/monthly", authenticate, getMonthlyReport);

module.exports = router;
