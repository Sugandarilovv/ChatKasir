const { supabaseAuth } = require("../config/supabase");

const authenticate = async (req, res, next) => {
  const authHeader = req.headers["authorization"];

  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return res
      .status(401)
      .json({ error: "Token tidak ditemukan, silakan login dulu" });
  }

  const token = authHeader.split(" ")[1];

  const { data, error } = await supabaseAuth.auth.getUser(token);

  if (error || !data.user) {
    return res
      .status(401)
      .json({ error: "Token tidak valid atau sudah expired" });
  }

  req.user = data.user;
  next();
};

module.exports = { authenticate };
