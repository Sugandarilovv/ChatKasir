const supabase = require("../config/supabase");

// POST /auth/register
const register = async (req, res) => {
  const { email, password, full_name } = req.body;

  // Validasi input sesuai API Contract
  if (!email || !password || !full_name) {
    return res.status(400).json({
      error: "Email, password, dan nama lengkap wajib diisi",
    });
  }

  // Daftar ke Supabase Auth
  const { data: authData, error: authError } = await supabase.auth.signUp({
    email,
    password,
  });

  if (authError) {
    return res.status(400).json({ error: authError.message });
  }

  const { error: profileError } = await supabase.from("users").insert({
    id: authData.user.id,
    full_name: full_name,
    avatar_url: null,
  });

  if (profileError) {
    return res.status(400).json({
      error: "Gagal simpan profil: " + profileError.message,
    });
  }

  return res.status(201).json({
    message: "Registrasi berhasil!",
    user: {
      id: authData.user.id,
      email: authData.user.email,
    },
  });
};

module.exports = { register };
