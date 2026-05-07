const express = require("express");
const cors = require("cors");
require("dotenv").config();

const authRoutes = require("./src/routes/authRoutes");
const transactionRoutes = require("./src/routes/transactionRoutes");

const app = express();
app.use(cors());
app.use(express.json());

app.use("/auth", authRoutes);
app.use("/transactions", transactionRoutes);

app.get("/", (req, res) => {
  res.json({ message: "ChatKasir API is running!" });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
