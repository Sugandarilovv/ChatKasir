import { useState, useRef, useEffect } from "react";
import MainLayout from "../components/layout/MainLayout";
import { useTheme } from "../context/ThemeContext";
import { getCurrentUser } from "../services/authService";
import { tanyaAI } from "../services/aiService";
import ReactMarkdown from 'react-markdown';

export default function TanyaAI() {
  const { theme } = useTheme();
  const isDark = theme === "dark";

  const [user, setUser] = useState({ nama: "Pengguna" });
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    try {
      const currentUser = getCurrentUser();
      if (currentUser && currentUser.nama) {
        setUser(currentUser);
      }
    } catch (error) {
      console.error("Gagal memuat data user", error);
    }
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const namaPanggilan = user.nama.split(" ")[0];

  async function handleSend(e) {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userText = input.trim();

    // Tampilkan pesan user ke layar
    setMessages((prev) => [...prev, { role: "user", text: userText }]);
    setInput("");
    setLoading(true);

    try {
      // 1. Format history agar sesuai dengan kebutuhan API Gemini (user dan model)
      const formattedHistory = messages.map((msg) => ({
        role: msg.role === "ai" ? "model" : "user",
        parts: [{ text: msg.text }],
      }));

      // 2. Panggil API AI sungguhan melalui fungsi di aiService
      const aiReply = await tanyaAI(formattedHistory, userText);

      // 3. Tampilkan balasan AI ke layar
      setMessages((prev) => [...prev, { role: "ai", text: aiReply }]);
    } catch (error) {
      // Tangani jika terjadi error koneksi / server
      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          text: "Maaf, terjadi kesalahan saat menghubungi AI. Silakan coba lagi.",
        },
      ]);
    } finally {
      // Matikan indikator loading
      setLoading(false);
    }
  }

  // --- WARNA TEMA (Tailwind v4 & CSS Variables) ---
  const bgUtama = isDark ? "#020617" : "#f8fafc";
  const textUtama = isDark ? "#f8fafc" : "#0f172a";
  const textMuda = isDark ? "#94a3b8" : "#64748b";
  const bgInput = isDark ? "#1e293b" : "#ffffff";
  const borderInp = isDark ? "#334155" : "#e2e8f0";

  return (
    <MainLayout>
      <div
        className="flex flex-col h-[calc(100vh-100px)] w-full max-w-4xl mx-auto rounded-3xl overflow-hidden relative"
        style={{ background: bgUtama, border: `1px solid ${borderInp}` }}
      >
        {/* AREA KONTEN (Tengah atau Chat) */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 custom-scrollbar relative">
          {messages.length === 0 ? (
            /* TAMPILAN AWAL */
            <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center animate-fade-in">
              <h1
                className="text-3xl sm:text-5xl font-bold mb-3"
                style={{ color: textUtama, letterSpacing: "-1px" }}
              >
                Halo, {namaPanggilan}
              </h1>
              <p
                className="text-sm sm:text-xl font-medium"
                style={{ color: textMuda }}
              >
                Apakah ada yang ingin ditanyakan hari ini?
              </p>
            </div>
          ) : (
            /* TAMPILAN PERCAKAPAN */
            <div className="space-y-6 pb-20">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-fade-up`}
                >
                  <div
                    className={`max-w-[85%] sm:max-w-[75%] p-4 rounded-2xl text-sm sm:text-base leading-relaxed ${
                      msg.role === "user"
                        ? "bg-green-600 text-white rounded-br-sm shadow-md"
                        : isDark
                          ? "bg-slate-800 text-slate-200 rounded-bl-sm border border-slate-700"
                          : "bg-white text-gray-800 rounded-bl-sm border border-gray-200 shadow-sm"
                    }`}
                  >
                    {/* Menggunakan parser Markdown untuk balasan AI agar rapi */}
                    {msg.role === "user" ? (
                      msg.text
                    ) : (
                      <ReactMarkdown
                        components={{
                          p: ({ node, ...props }) => <p className="mb-2 last:mb-0" {...props} />,
                          ul: ({ node, ...props }) => <ul className="list-disc pl-5 mb-2 space-y-1" {...props} />,
                          ol: ({ node, ...props }) => <ol className="list-decimal pl-5 mb-2 space-y-1" {...props} />,
                          li: ({ node, ...props }) => <li className="text-sm sm:text-base" {...props} />,
                          strong: ({ node, ...props }) => <strong className="font-bold text-green-500 dark:text-green-400" {...props} />,
                        }}
                      >
                        {msg.text}
                      </ReactMarkdown>
                    )}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex justify-start animate-fade-in">
                  <div
                    className={`p-4 rounded-2xl rounded-bl-sm flex gap-2 items-center ${isDark ? "bg-slate-800 border-slate-700" : "bg-white border-gray-200 shadow-sm"} border`}
                  >
                    <span
                      className="w-2 h-2 rounded-full bg-green-500 animate-bounce"
                      style={{ animationDelay: "0ms" }}
                    />
                    <span
                      className="w-2 h-2 rounded-full bg-green-500 animate-bounce"
                      style={{ animationDelay: "150ms" }}
                    />
                    <span
                      className="w-2 h-2 rounded-full bg-green-500 animate-bounce"
                      style={{ animationDelay: "300ms" }}
                    />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* AREA INPUT DI BAWAH */}
        <div className="p-3 sm:p-5" style={{ background: bgUtama }}>
          <form
            onSubmit={handleSend}
            className="flex items-end gap-2 p-1.5 sm:p-2 rounded-2xl sm:rounded-full transition-all"
            style={{
              background: bgInput,
              border: `1.5px solid ${borderInp}`,
              boxShadow: "0 10px 25px -5px rgba(0,0,0,0.05)",
            }}
          >
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend(e);
                }
              }}
              placeholder="Tanya apa saja..."
              className="flex-1 bg-transparent border-none outline-none resize-none px-4 py-3 min-h-12 max-h-30 text-sm sm:text-base custom-scrollbar"
              style={{ color: textUtama }}
              rows={1}
            />

            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="w-10 h-10 sm:w-12 sm:h-12 shrink-0 flex items-center justify-center rounded-full text-white transition-all disabled:opacity-40 disabled:cursor-not-allowed mb-0.5 mr-0.5"
              style={{
                background:
                  input.trim() && !loading
                    ? "#16a34a"
                    : isDark
                      ? "#334155"
                      : "#cbd5e1",
              }}
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </form>
          <p
            className="text-center text-[10px] sm:text-xs mt-3"
            style={{ color: textMuda }}
          >
            AI dapat membuat kesalahan. Harap periksa kembali informasi penting.
          </p>
        </div>
      </div>
    </MainLayout>
  );
}