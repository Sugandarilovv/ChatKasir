const express = require("express");
const cors = require("cors");
require("dotenv").config();

const authRoutes = require("./src/routes/authRoutes");
const transactionRoutes = require("./src/routes/transactionRoutes");
const reportRoutes = require("./src/routes/reportRoutes");
const userRoutes = require("./src/routes/userRoutes");
const tanyaAIRoutes = require("./src/routes/tanyaAIRoutes");

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

      if (
        !origin ||
        cleanOrigins.includes(cleanOrigin) ||
        cleanOrigin.endsWith(".vercel.app")
      ) {
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

app.use(express.json());

app.use("/auth", authRoutes);
app.use("/transactions", transactionRoutes);
app.use("/report", reportRoutes);
app.use("/users", userRoutes);
app.use('/tanya-ai', tanyaAIRoutes);

app.get("/", (req, res) => {
  res.json({ message: "ChatKasir API is running!" });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));

module.exports = app;
