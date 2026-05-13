const request = require("supertest");
const express = require("express");
require("dotenv").config();

const authRoutes = require("../src/routes/authRoutes");

const app = express();
app.use(express.json());
app.use("/auth", authRoutes);

describe("POST /auth/register", () => {
  test("gagal jika field tidak lengkap", async () => {
    const res = await request(app)
      .post("/auth/register")
      .send({ email: "test@gmail.com" });

    expect(res.statusCode).toBe(400);
    expect(res.body).toHaveProperty("errors");
  });

  test("gagal jika format email salah", async () => {
    const res = await request(app)
      .post("/auth/register")
      .send({ email: "bukan-email", password: "123456", full_name: "Test" });

    expect(res.statusCode).toBe(400);
  });
});

describe("POST /auth/login", () => {
  test("gagal jika field kosong", async () => {
    const res = await request(app).post("/auth/login").send({});

    expect(res.statusCode).toBe(400);
    expect(res.body).toHaveProperty("error");
  });

  test("gagal jika email atau password salah", async () => {
    const res = await request(app)
      .post("/auth/login")
      .send({ email: "salah@gmail.com", password: "salah123" });

    expect(res.statusCode).toBe(401);
  });
});
