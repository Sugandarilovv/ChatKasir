const { supabase } = require("../config/supabase");

// GET /users/profile — buat ambil data profil user yang sedang login
const getProfile = async (req, res) => {
  const userId = req.user.id;

  const { data, error } = await supabase
    .from("users")
    .select("id, full_name, avatar_url")
    .eq("id", userId)
    .single();

  if (error) return res.status(400).json({ error: error.message });
  return res.status(200).json({ data });
};

// PUT /users/profile — buat update nama dan/atau foto
const updateProfile = async (req, res) => {
  const userId = req.user.id;
  const { full_name, avatar_url } = req.body;

  const updateData = {};
  if (full_name !== undefined) updateData.full_name = full_name;
  if (avatar_url !== undefined) updateData.avatar_url = avatar_url;

  if (Object.keys(updateData).length === 0) {
    return res.status(400).json({ error: "Tidak ada data yang diperbarui." });
  }

  const { data, error } = await supabase
    .from("users")
    .update(updateData)
    .eq("id", userId)
    .select();

  if (error) return res.status(400).json({ error: error.message });
  return res.status(200).json({ message: "Profil berhasil diperbarui", data });
};

// DELETE /users/account — untuk hapus akun permanen
const deleteAccount = async (req, res) => {
  const userId = req.user.id;

  try {
    const { error: dbError } = await supabase
      .from("users")
      .delete()
      .eq("id", userId);

    if (dbError) throw dbError;

    const { error: authError } = await supabase.auth.admin.deleteUser(userId);

    if (authError) throw authError;

    return res.status(200).json({
      message: "Akun dan seluruh data berhasil dihapus secara permanen.",
    });
  } catch (error) {
    return res.status(400).json({ error: error.message });
  }
};

module.exports = { getProfile, updateProfile, deleteAccount };
