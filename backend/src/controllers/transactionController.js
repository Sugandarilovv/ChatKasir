const supabase = require("../config/supabase");

const callAIExtract = async (text) => {
  // --- MOCKING (Data Palsu Sementara) ---
  console.log("Menerima teks:", text);
  console.log("Pura-puranya AI Denny lagi mikir...");

  //skenario pura pura
  return {
    status: "success",
    predictions: [
      {
        product_name: "Kopi Susu Gula Aren",
        quantity: 2,
        price_satuan: 15000,
        confidence: "HIGH",
      },
    ],
  };
};

// POST /transactions
const createTransaction = async (req, res) => {
  const { raw_text } = req.body;
  const user_id = req.user.id; // dari authMiddleware

  // Validasi input
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

  if (
    aiResponse.status === "failed" ||
    !aiResponse.predictions ||
    aiResponse.predictions.length === 0
  ) {
    await supabase
      .from("chat_extractions")
      .update({ status: "failed" })
      .eq("id", extraction.id);

    return res
      .status(422)
      .json({ error: "Teks tidak dapat diekstrak oleh AI" });
  }

  const transactionItems = aiResponse.predictions.map((item) => ({
    extraction_id: extraction.id,
    user_id,
    product_name: item.product_name,
    quantity: item.quantity,
    price_satuan: item.price_satuan,
    total: item.price_satuan * item.quantity,
    confidence: item.confidence,
    is_manual: false,
    transaction_date: new Date().toISOString().split("T")[0],
  }));

  const { data: transactions, error: transactionError } = await supabase
    .from("transactions")
    .insert(transactionItems)
    .select();

  if (transactionError) {
    return res.status(500).json({
      error: "Gagal menyimpan transaksi: " + transactionError.message,
    });
  }

  await supabase
    .from("chat_extractions")
    .update({ status: "processed" })
    .eq("id", extraction.id);

  return res.status(201).json({
    message: "Transaksi berhasil diekstrak dan disimpan",
    data: transactions,
  });
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
};
