const express = require("express");
const router = express.Router();
const { authenticate } = require("../middleware/authMiddleware");
const { createTransaction } = require("../controllers/transactionController");
const { getTransactions } = require("../controllers/transactionController");

router.post("/", authenticate, createTransaction);
router.get("/", authenticate, getTransactions);

module.exports = router;
