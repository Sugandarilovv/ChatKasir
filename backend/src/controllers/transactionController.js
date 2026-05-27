const { supabase } = require("../config/supabase");

const callAIExtract = async (text) => {
  try {
    // coba health check — TANPA API key
    const health = await fetch(`${process.env.AI_API_URL}/health`);
    const healthData = await health.json();
    console.log("Health:", healthData);
    console.log("AI_API_URL:", process.env.AI_API_URL);
    console.log("AI_API_KEY:", process.env.AI_API_KEY?.substring(0, 5) + "...");

    if (!healthData.model_loaded) {
      console.warn("Model belum ready");
      return { status: "failed", predictions: [] };
    }

    // predict — DENGAN API key
    const response = await fetch(`${process.env.AI_API_URL}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": process.env.AI_API_KEY,
      },
      body: JSON.stringify({ raw_text: text }),
    });

    if (!response.ok) {
      const errData = await response.json();
      console.error("AI API error:", errData);
      return { status: "failed", predictions: [] };
    }

    const data = await response.json();
    console.log("Response dari AI:", JSON.stringify(data));

    const predictions = (data.results || []).map((item) => ({
      product_name: item.product,
      quantity: item.quantity,
      price_satuan: item.price_satuan,
      total: item.total,
      confidence: item.confidence,
    }));

    return { status: "success", predictions };
  } catch (err) {
    console.error("Tidak bisa konek ke AI API:", err.message);
    return { status: "failed", predictions: [] };
  }
};

// POST /transactions/analyze - buat analisa AI, blm masuk ke tabel transactions
const analyzeTransaction = async (req, res) => {
  const { raw_text } = req.body;
  const user_id = req.user.id;

  if (!raw_text || raw_text.trim() === "") {
    return res.status(400).json({ error: "Teks chat tidak boleh kosong" });
  }

  const { data: extraction, error: extractionError } = await supabase
    .from("chat_extractions")
    .insert([{ raw_text, user_id, status: "pending" }])
    .select()
    .single();

  if (extractionError) {
    return res.status(500).json({
      error: "Gagal menyimpan riwayat chat: " + extractionError.message,
    });
  }

  const aiResponse = await callAIExtract(raw_text);

  if (!aiResponse.predictions || aiResponse.predictions.length === 0) {
    await supabase
      .from("chat_extractions")
      .update({ status: "failed" })
      .eq("id", extraction.id);
    return res
      .status(422)
      .json({ error: "Teks tidak dapat diekstrak oleh AI" });
  }

  await supabase
    .from("chat_extractions")
    .update({ status: "processed" })
    .eq("id", extraction.id);

  return res.status(200).json({
    message: "Teks berhasil dianalisis oleh AI",
    extraction_id: extraction.id,
    predictions: aiResponse.predictions,
  });
};

// POST /transactions — tuk menyimpan data transaksi yang sudah dikonfirmasi/fix dari Frontend
const createTransaction = async (req, res) => {
  const user_id = req.user.id;
  const { extraction_id, products } = req.body;

  if (!extraction_id) {
    return res.status(400).json({ error: "extraction_id tidak boleh kosong" });
  }
  if (!products || !Array.isArray(products) || products.length === 0) {
    return res
      .status(400)
      .json({ error: "Daftar produk tidak valid atau kosong" });
  }

  try {
    const transactionItems = products.map((item) => ({
      extraction_id: extraction_id,
      user_id: user_id,
      product_name: item.product_name,
      quantity: item.quantity,
      price_satuan: item.price_satuan,
      total: item.total,
      confidence: item.confidence || "HIGH",
      is_manual: item.is_manual || false,
      transaction_date: new Date().toISOString().split("T")[0],
    }));

    const { data: transactions, error: transactionError } = await supabase
      .from("transactions")
      .insert(transactionItems)
      .select();

    if (transactionError) {
      throw transactionError;
    }

    return res.status(201).json({
      message: "Transaksi berhasil dikonfirmasi dan disimpan permanen",
      data: transactions,
    });
  } catch (error) {
    return res.status(500).json({
      error: "Gagal menyimpan transaksi: " + error.message,
    });
  }
};

// GET /transactions (dengan filter & paginasi)
const getTransactions = async (req, res) => {
  const user_id = req.user.id;
  const { startDate, endDate, page = 1, limit = 10 } = req.query;

  // Hitung range untuk paginasi
  const from = (page - 1) * limit;
  const to = from + limit - 1;

  try {
    let query = supabase
      .from("transactions")
      .select("*", { count: "exact" }) // count: untuk tau jumlah total data buat pagination di Frontend
      .eq("user_id", user_id)
      .order("transaction_date", { ascending: false })
      .range(from, to);

    // nambahin filter tanggal
    if (startDate) query = query.gte("transaction_date", startDate);
    if (endDate) query = query.lte("transaction_date", endDate);

    const { data, error, count } = await query;

    if (error) throw error;

    return res.status(200).json({
      message: "Data transaksi berhasil diambil",
      pagination: {
        total_items: count,
        current_page: parseInt(page),
        total_pages: Math.ceil(count / limit),
        limit: parseInt(limit),
      },
      data,
    });
  } catch (error) {
    return res
      .status(500)
      .json({ error: "Gagal mengambil data: " + error.message });
  }
};

module.exports = {
  createTransaction,
  getTransactions,
  analyzeTransaction,
};
