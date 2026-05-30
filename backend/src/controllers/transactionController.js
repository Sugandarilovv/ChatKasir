const { supabase } = require("../config/supabase");

// fungsi manggil AI
const callAIExtract = async (text) => {
  try {
    // coba health check — tanpa API key
    const health = await fetch(`${process.env.AI_API_URL}/health`);
    const healthData = await health.json();
    console.log("Health:", healthData);
    console.log("AI_API_URL:", process.env.AI_API_URL);
    console.log("AI_API_KEY:", process.env.AI_API_KEY?.substring(0, 5) + "...");

    if (!healthData.model_loaded) {
      console.warn("Model belum ready");
      return {
        status: "failed",
        results: [],
        total_akumulasi: 0,
        clean_text: text,
      };
    }

    // predict — dengan API key
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
      return {
        status: "failed",
        results: [],
        total_akumulasi: 0,
        clean_text: text,
      };
    }

    const data = await response.json();
    console.log("Response dari AI:", JSON.stringify(data));

    const results = (data.results || []).map((item) => ({
      product_name: item.product_name,
      quantity: item.quantity,
      price_satuan: item.price_satuan,
      subtotal: item.subtotal,
      confidence: item.confidence,
    }));

    return {
      status: "success",
      results: results,
      total_akumulasi: data.total_akumulasi || 0,
      clean_text: data.clean_text || text,
    };
  } catch (err) {
    console.error("Tidak bisa konek ke AI API:", err.message);
    return {
      status: "failed",
      results: [],
      total_akumulasi: 0,
      clean_text: text,
    };
  }
};

// POST /transactions/analyze - buat analisa AI
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

  if (!aiResponse.results || aiResponse.results.length === 0) {
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
    results: aiResponse.results,
    total_akumulasi: aiResponse.total_akumulasi,
  });
};

// POST /transactions — tuk menyimpan data permanen
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
      total: item.subtotal || item.total,
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

  const from = (page - 1) * limit;
  const to = from + limit - 1;

  try {
    let query = supabase
      .from("transactions")
      .select("*", { count: "exact" })
      .eq("user_id", user_id)
      .order("transaction_date", { ascending: false })
      .range(from, to);

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

// GET /transactions/report — utk suplai data ke dashboard frontend
const getDashboardReport = async (req, res) => {
  const user_id = req.user.id;
  const { startDate, endDate } = req.query;

  if (!startDate || !endDate) {
    return res.status(400).json({
      error:
        "Query startDate dan endDate wajib diisi. Contoh: ?startDate=2026-05-01&endDate=2026-05-07",
    });
  }

  try {
    const { data: transactions, error } = await supabase
      .from("transactions")
      .select("*")
      .eq("user_id", user_id)
      .gte("transaction_date", startDate)
      .lte("transaction_date", endDate)
      .order("created_at", { ascending: false });

    if (error) throw error;

    let totalRevenue = 0;
    let totalItemsSold = 0;
    const uniqueTransactions = new Set();
    const uniqueDays = new Set();
    const dailyRevenue = {};
    const productStats = {};

    transactions.forEach((item) => {
      totalRevenue += item.total;
      totalItemsSold += item.quantity;

      uniqueTransactions.add(item.extraction_id);
      uniqueDays.add(item.transaction_date);

      const date = item.transaction_date;
      if (!dailyRevenue[date]) dailyRevenue[date] = 0;
      dailyRevenue[date] += item.total;

      const product = item.product_name;
      if (!productStats[product]) {
        productStats[product] = { total_sold: 0, total_revenue: 0 };
      }
      productStats[product].total_sold += item.quantity;
      productStats[product].total_revenue += item.total;
    });

    const totalTransactions = uniqueTransactions.size;
    const totalDaysCount = uniqueDays.size;

    const averageOrderValue =
      totalTransactions > 0 ? totalRevenue / totalTransactions : 0;
    const averageRevenuePerDay =
      totalDaysCount > 0 ? totalRevenue / totalDaysCount : 0;

    const chartData = Object.keys(dailyRevenue)
      .map((date) => ({
        date: date,
        revenue: dailyRevenue[date],
      }))
      .sort((a, b) => new Date(a.date) - new Date(b.date));

    const topProducts = Object.keys(productStats)
      .map((name) => ({
        name: name,
        total_sold: productStats[name].total_sold,
        total_revenue_generated: productStats[name].total_revenue,
      }))
      .sort((a, b) => b.total_revenue_generated - a.total_revenue_generated)
      .slice(0, 5);

    return res.status(200).json({
      message: "Data laporan dashboard berhasil di-generate",
      summary: {
        total_revenue: totalRevenue,
        total_transactions: totalTransactions,
        total_items_sold: totalItemsSold,
        average_order_value: averageOrderValue,
        average_revenue_per_day: averageRevenuePerDay,
      },
      chart_data: chartData,
      top_products: topProducts,
      transactions: transactions,
    });
  } catch (error) {
    return res
      .status(500)
      .json({ error: "Gagal memproses laporan: " + error.message });
  }
};

module.exports = {
  createTransaction,
  getTransactions,
  analyzeTransaction,
  getDashboardReport,
};
