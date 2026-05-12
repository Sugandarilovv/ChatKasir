const { supabase, supabaseAuth } = require("../config/supabase");
const { validationResult } = require("express-validator");

const register = async (req, res) => {
  // Cek hasil validasi
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  const { email, password, full_name } = req.body;

  const { data: authData, error: authError } = await supabaseAuth.auth.signUp({
    email,
    password,
    options: { data: { full_name } },
  });

  if (authError) return res.status(400).json({ error: authError.message });

  // Simpan ke tabel users kita
  await supabase.from("users").insert({
    id: authData.user.id,
    full_name: full_name,
  });

  return res.status(201).json({
    message: "Registrasi berhasil! Silakan cek email untuk kode OTP.",
  });
};

const verifyOtp = async (req, res) => {
  const { email, token } = req.body; // Token itu kode OTP 6 digit

  const { data, error } = await supabaseAuth.auth.verifyOtp({
    email,
    token,
    type: "signup",
  });

  if (error) return res.status(400).json({ error: error.message });
  return res
    .status(200)
    .json({ message: "Email berhasil diverifikasi!", session: data.session });
};

// POST /auth/login
const login = async (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({
      error: "Email dan password wajib diisi",
    });
  }

  const { data, error } = await supabaseAuth.auth.signInWithPassword({
    email,
    password,
  });

  if (error) {
    return res.status(401).json({
      error: "Email atau password salah",
    });
  }

  return res.status(200).json({
    message: "Login berhasil",
    token: data.session.access_token,
    user_id: data.user.id,
  });
};

module.exports = {
  register,
  login,
  verifyOtp,
};
