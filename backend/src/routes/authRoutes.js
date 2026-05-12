const express = require("express");
const router = express.Router();
const { body } = require("express-validator");
const { register, login, verifyOtp } = require("../controllers/authController");

// Validasi untuk Register
const registerValidation = [
  body("email").isEmail().withMessage("Format email tidak valid"),
  body("password")
    .isLength({ min: 6 })
    .withMessage("Password minimal 6 karakter"),
  body("full_name").notEmpty().withMessage("Nama lengkap wajib diisi"),
];

router.post("/register", registerValidation, register);
router.post("/login", login);
router.post("/verify-otp", verifyOtp);

module.exports = router;
