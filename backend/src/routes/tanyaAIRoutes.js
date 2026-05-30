const express = require("express");
const router = express.Router();
const { GoogleGenerativeAI } = require("@google/generative-ai");

router.post("/", async (req, res) => {
  try {
    const { history, message } = req.body;

    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      return res
        .status(500)
        .json({ error: "API Key Gemini belum disetting di server Vercel." });
    }

    const genAI = new GoogleGenerativeAI(apiKey);

    // 🔥 TAMBAHKAN SYSTEM INSTRUCTION DI SINI UNTUK MEMBATASI TOPIK
    const model = genAI.getGenerativeModel({
      model: "gemini-3.1-flash-lite", // Pastikan versi model ini yang mau dipakai ya!
      systemInstruction: `
        Anda adalah ChatBot bernama TanyaAI, asisten ahli di bidang Ekonomi, Bisnis, Keuangan, dan UMKM Indonesia.
        
        ATURAN KETAT:
        1. Jika pengguna HANYA menyapa (misal: "halo", "hai", "test", "selamat pagi"), balaslah sapaan tersebut dengan ramah dan tawarkan bantuan seputar bisnis/UMKM.
        2. Jika pengguna bertanya topik ekonomi, akuntansi, stok, kasir, pemasaran, atau UMKM, berikan jawaban solutif, ramah, dan profesional.
        3. Jika pengguna bertanya topik DI LUAR bisnis/UMKM (seperti politik, agama, olahraga, koding, dll), tolak dengan sopan dan kembalikan topik ke seputar UMKM.
      `,
    });

    // Mulai sesi chat dengan membawa history dari frontend
    const chat = model.startChat({ history: history || [] });

    // Kirim pesan baru user ke Gemini
    const result = await chat.sendMessage(message);
    const response = await result.response;

    // Kembalikan teks balasan ke frontend
    res.json({ reply: response.text() });
  } catch (error) {
    console.error("Gemini Error:", error);
    res.status(500).json({ error: "Gagal memproses permintaan AI." });
  }
});

module.exports = router;
