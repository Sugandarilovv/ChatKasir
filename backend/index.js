const express = require("express");
const cors = require("cors");
require("dotenv").config();

const authRoutes = require("./src/routes/authRoutes");
const transactionRoutes = require("./src/routes/transactionRoutes");
const reportRoutes = require("./src/routes/reportRoutes");
const userRoutes = require("./src/routes/userRoutes");

const app = express();

app.use(
  cors({
    origin: function (origin, callback) {
      const allowedOrigins = [
        "http://localhost:5173",
        "http://localhost:3000",
        process.env.FRONTEND_URL,
      ];

      const cleanOrigins = allowedOrigins.map((url) =>
        url ? url.replace(/\/$/, "") : url,
      );
      const cleanOrigin = origin ? origin.replace(/\/$/, "") : origin;

      // buat bersihin tanda slash
      if (
        !origin ||
        cleanOrigins.includes(cleanOrigin) ||
        cleanOrigin.endsWith(".vercel.app")
      ) {
        // Baris ".endsWith" di atas otomatis mengizinkan semua domain vercel milik Alfan termasuk link preview-nya!
        callback(null, true);
      } else {
        console.log("Origin yang diblokir oleh CORS:", origin);
        callback(new Error("Not allowed by CORS"));
      }
    },
    methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"],
    credentials: true,
  }),
);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
