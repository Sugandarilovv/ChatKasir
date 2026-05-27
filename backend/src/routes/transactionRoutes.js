const express = require("express");
const router = express.Router();
const { authenticate } = require("../middleware/authMiddleware");
const {
  analyzeTransaction,
  createTransaction,
  getTransactions,
  getDashboardReport,
} = require("../controllers/transactionController");

router.post("/analyze", authenticate, analyzeTransaction);
router.post("/", authenticate, createTransaction);
router.get("/", authenticate, getTransactions);
router.get("/report", authenticate, getDashboardReport);

module.exports = router;
