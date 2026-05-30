const express = require('express');
const router = express.Router();
const { GoogleGenerativeAI } = require('@google/generative-ai');

router.post('/', async (req, res) => {
    try {
        const { history, message } = req.body;

        const apiKey = process.env.GEMINI_API_KEY;
        if (!apiKey) {
            return res.status(500).json({ error: "API Key Gemini belum disetting di server Vercel." });
        }

        const genAI = new GoogleGenerativeAI(apiKey);

        // 🔥 TAMBAHKAN SYSTEM INSTRUCTION DI SINI UNTUK MEMBATASI TOPIK
        const model = genAI.getGenerativeModel({
            model: "gemini-3.1-flash-lite",
            systemInstruction: `
        Anda adalah ChatBot bernama TanyaAI, seorang asisten ahli khusus di bidang Ekonomi, Bisnis, Keuangan, dan Usaha Mikro Kecil Menengah (UMKM) Indonesia.
        
        ATURAN KETAT:
        1. Anda HANYA boleh menjawab pertanyaan yang berkaitan dengan ekonomi, keuangan, strategi bisnis, pemasaran, akuntansi, pengelolaan stok, kasir, dan pengembangan UMKM.
        2. Gunakan bahasa Indonesia yang ramah, profesional, mudah dipahami oleh pemilik toko/pedagang kecil, dan solutif.
        3. Jika pengguna bertanya tentang topik di luar ekonomi dan UMKM (seperti politik, gosip artis, olahraga, sains fiksi, koding software umum, agama, atau sejarah non-ekonomi), jawablah dengan sopan bahwa Anda tidak bisa menjawabnya karena tugas Anda dikhususkan untuk membantu pertumbuhan bisnis dan UMKM.
        
        Contoh penolakan: "Maaf, sebagai asisten TanyaAI, saya hanya dikhususkan untuk membantu Anda dalam mengelola bisnis, strategi UMKM, dan topik seputar ekonomi. Apakah ada yang bisa saya bantu terkait usaha Anda?"
      `
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