const express = require("express");
const router = express.Router();
const { body } = require("express-validator");
const {
  register,
  login,
  verifyOtp,
  forgotPassword,
  updatePassword,
} = require("../controllers/authController");

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
router.post("/forgot-password", forgotPassword);

router.put("/update-password", updatePassword);

module.exports = router;
