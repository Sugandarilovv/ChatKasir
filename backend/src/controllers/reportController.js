const supabase = require("../config/supabase");

// GET /report/monthly
const getMonthlyReport = async (req, res) => {
  const user_id = req.user.id;

  // untuk ambil query bulan dan tahun
  const { month = new Date().getMonth() + 1, year = new Date().getFullYear() } =
    req.query;

  const startDate = new Date(year, month - 1, 1).toISOString().split("T")[0];
  const endDate = new Date(year, month, 0).toISOString().split("T")[0];

  try {
    const { data, error } = await supabase
      .from("transactions")
      .select("product, quantity, total, transaction_date")
      .eq("user_id", user_id)
      .gte("transaction_date", startDate)
      .lte("transaction_date", endDate);

    if (error) throw error;

    // Hitung ringkasan
    let total_revenue = 0;
    let total_items_sold = 0;

    data.forEach((item) => {
      total_revenue += Number(item.total);
      total_items_sold += Number(item.quantity);
    });

    return res.status(200).json({
      message: "Laporan bulanan berhasil diambil",
      period: `${month}-${year}`,
      summary: {
        total_revenue,
        total_items_sold,
        total_transactions: data.length,
      },
      data,
    });
  } catch (error) {
    return res
      .status(500)
      .json({ error: "Gagal mengambil laporan: " + error.message });
  }
};

module.exports = { getMonthlyReport };
