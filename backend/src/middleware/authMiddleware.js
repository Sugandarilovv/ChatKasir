const { supabaseAuth } = require("../config/supabase");

const authenticate = async (req, res, next) => {
  // Ambil token dari header Authorization
  const authHeader = req.headers["authorization"];

  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return res
      .status(401)
      .json({ error: "Token tidak ditemukan, silakan login dulu" });
  }

  const token = authHeader.split(" ")[1];

  // Verifikasi token ke Supabase
  const { data, error } = await supabaseAuth.auth.getUser(token);

  if (error || !data.user) {
    return res
      .status(401)
      .json({ error: "Token tidak valid atau sudah expired" });
  }

  // Simpan data user ke req supaya bisa dipakai di controller
  req.user = data.user;
  next();
};

module.exports = { authenticate };
