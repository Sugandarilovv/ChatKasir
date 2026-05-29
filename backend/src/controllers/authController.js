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
    message:
      "Registrasi berhasil! Silakan cek email untuk verifikasi lebih lanjut.",
  });
};

const verifyOtp = async (req, res) => {
  const { email, token } = req.body;

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

// POST /auth/forgot-password
const forgotPassword = async (req, res) => {
  const { email } = req.body;

  if (!email) {
    return res.status(400).json({ error: "Email wajib diisi" });
  }

  const frontendUrl = process.env.FRONTEND_URL?.replace(/\/$/, "");

  const { error } = await supabaseAuth.auth.resetPasswordForEmail(email, {
    redirectTo: `${frontendUrl}/lupa-password`,
  });

  if (error) {
    return res.status(400).json({ error: error.message });
  }

  return res.status(200).json({
    message: "Link reset password sudah dikirim ke email kamu",
  });
};

// PUT /auth/update-password
const updatePassword = async (req, res) => {
  const { access_token, refresh_token, new_password } = req.body;

  if (!access_token || !refresh_token || !new_password) {
    return res.status(400).json({
      error: "Access token, refresh token, dan password baru wajib diisi",
    });
  }

  if (new_password.length < 8) {
    return res.status(400).json({
      error: "Password minimal 8 karakter",
    });
  }

  const { error: sessionError } = await supabaseAuth.auth.setSession({
    access_token,
    refresh_token,
  });

  if (sessionError) {
    return res
      .status(401)
      .json({ error: "Token tidak valid atau sudah expired" });
  }

  // Update password
  const { error } = await supabaseAuth.auth.updateUser({
    password: new_password,
  });

  if (error) {
    return res.status(400).json({ error: error.message });
  }

  return res.status(200).json({
    message: "Password berhasil diperbarui, silakan login dengan password baru",
  });
};

module.exports = { register, login, verifyOtp, forgotPassword, updatePassword };
