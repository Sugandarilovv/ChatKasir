const { createClient } = require("@supabase/supabase-js");
require("dotenv").config();

// Untuk operasi database
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SECRET_KEY,
);

// Untuk operasi auth (verifikasi token, login, register)
const supabaseAuth = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_PUBLISHABLE_KEY,
);

module.exports = { supabase, supabaseAuth };
