const supabase = require("../config/supabase");

// POST /auth/register
const register = async (req, res) => {
  const { email, password, full_name } = req.body;

  if (!email || !password || !full_name) {
    return res.status(400).json({
      error: "Email, password, dan nama lengkap wajib diisi",
    });
  }

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

// POST /auth/login
const login = async (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({
      error: "Email dan password wajib diisi",
    });
  }

  const { data, error } = await supabase.auth.signInWithPassword({
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

module.exports = { register, login };
