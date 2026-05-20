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
    origin: [
      "http://localhost:5173", // ← development frontend
      "http://localhost:3000", // ← development lokal
    ],
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

app.get("/", (req, res) => {
  res.json({ message: "ChatKasir API is running!" });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
