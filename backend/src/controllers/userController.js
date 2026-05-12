const supabase = require("../config/supabase");

const updateProfile = async (req, res) => {
  const userId = req.user.id; // Ambil dari middleware auth
  const { full_name, avatar_url } = req.body;

  const { data, error } = await supabase
    .from("users")
    .update({ full_name, avatar_url })
    .eq("id", userId)
    .select();

  if (error) return res.status(400).json({ error: error.message });
  return res.status(200).json({ message: "Profil berhasil diperbarui", data });
};

module.exports = {
  register,
  login,
  verifyOtp,
};
