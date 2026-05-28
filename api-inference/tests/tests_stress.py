"""
Stress test — Kirim 100 request beruntun secara paralel ke POST /predict.
Mengukur metrik Latency P50, P95, P99, Throughput, dan Delta Kebocoran Memori (RAM).

Cara Eksekusi Manual:
    cd api-inference
    python tests/tests_stress.py --url http://localhost:7860 --api-key changeme
"""

from __future__ import annotations

import argparse
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import MagicMock, patch

import pytest

# ── Payload Fixtures (Diselaraskan dengan Ekosistem Chat Riil V2) ─────────────

STRESS_PAYLOADS = [
    # Skenario 1: Chat Majemuk Katering Skala Besar
    "[28/05, 05:26] Rifan: order paket ayam bakar madu 10 pack sama es kopi susu gula aren 5 cup\n"
    "[28/05, 06:01] Alfan: siap harganya 35k dan es kopi harganya 18k jadi total katering semuanya 440000",

    # Skenario 2: Konfirmasi Harga Tanpa Total Nominal Akhir
    "[08.00, 22/04] Pembeli Lama: pesan 3 es teh manis\n"
    "[08.01, 22/04] Kasir: oke kak es teh harganya 5ribu ya",

    # Skenario 3: Ketikan Singkat Penuh Kata Slang / Noise Tulis
    "[07.42] Rifan: bg psnnn nasgorrrr ayam 2 porsi gede dnk\n"
    "[07.44] Alfan: siap mas bro harga 15000",

    # Skenario 4: Kasus Kesalahan Nota Klaim Kasir (Mismatch Zone)
    "[09.00] Pelanggan: mau 2 ayam bakar jumbo\n"
    "[09.01] Toko: ayam bakar 15000 total tagihan katering 25000 ya",

    # Skenario 5: Edge Case - Konfirmasi Harga Absen/Belum Siap
    "[10.00] Rifan: pesan 1 jus alpukat segar\n"
    "[10.01] Alfan: oke kak nanti saya cek dulu harganya di nota"
]

N_REQUESTS    = 100
MAX_WORKERS   = 10       # Batas maksimum thread pekerja paralel
P95_TARGET_MS = 500.0    # Batas toleransi latensi target: P95 ≤ 500ms
ERROR_RATE_MAX = 0.0     # Target mutlak: 0% eror kegagalan sistem


# ── Core Runner Engine ────────────────────────────────────────────────────────

def _send_request(
    base_url: str,
    api_key: str,
    payload: str,
) -> tuple[int, float]:
    """
    Kirim satu POST request /predict. 
    Membuka instans httpx.Client lokal per thread untuk menjamin status THREAD-SAFE.
    """
    import httpx
    
    # Bungkus secara lokal untuk menghindari interferensi soket antar thread paralel
    with httpx.Client() as client:
        t0 = time.perf_counter()
        try:
            resp = client.post(
                f"{base_url}/predict",
                json={"raw_text": payload},
                headers={"X-API-Key": api_key},
                timeout=30.0,
            )
            status_code = resp.status_code
        except Exception:
            status_code = 500  # Terjemahkan kegagalan koneksi sebagai eror internal
            
        elapsed_ms = (time.perf_counter() - t0) * 1000
        
    return status_code, elapsed_ms


def run_stress_test(
    base_url: str = "http://localhost:7860",  # 🌟 Diperbarui ke default port 7860
    api_key: str  = "changeme",
    n: int        = N_REQUESTS,
    workers: int  = MAX_WORKERS,
) -> dict:
    """
    Eksekutor penembak beban massal simultan ke endpoint REST API.
    """
    try:
        import httpx
    except ImportError:
        raise RuntimeError("Pustaka httpx wajib terpasang: pip install httpx")

    try:
        import psutil
        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024  # Konversi ke satuan MB
    except ImportError:
        mem_before = None

    results: list[tuple[int, float]] = []
    payloads = [STRESS_PAYLOADS[i % len(STRESS_PAYLOADS)] for i in range(n)]

    # Jalankan kolam manajemen thread untuk simulasi serbuan multi-klien
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(_send_request, base_url, api_key, p)
            for p in payloads
        ]
        for fut in as_completed(futures):
            results.append(fut.result())

    status_codes = [r[0] for r in results]
    times_ms     = [r[1] for r in results]

    # Anggap HTTP code selain 200 (Sukses) dan 422 (Gagal Validasi Karakter) sebagai Malfungsi
    errors     = sum(1 for s in status_codes if s not in (200, 422))
    error_rate = errors / n

    sorted_times = sorted(times_ms)
    p50 = statistics.median(sorted_times)
    p95 = sorted_times[int(n * 0.95)] if n > 0 else 0
    p99 = sorted_times[int(n * 0.99)] if n > 0 else 0

    if mem_before is not None:
        import psutil
        mem_after = psutil.Process().memory_info().rss / 1024 / 1024
        mem_delta = mem_after - mem_before
    else:
        mem_delta = None

    return {
        "n":            n,
        "workers":      workers,
        "errors":       errors,
        "error_rate":   error_rate,
        "min_ms":       min(times_ms) if times_ms else 0,
        "max_ms":       max(times_ms) if times_ms else 0,
        "median_ms":    p50,
        "p95_ms":       p95,
        "p99_ms":       p99,
        "mem_delta_mb": mem_delta,
        "status_counts": {str(s): status_codes.count(s) for s in set(status_codes)},
    }


def print_results(r: dict) -> bool:
    print("\n" + "=" * 55)
    print("  STRESS TEST RESULTS — ChatKasir API-2 (V2 STABLE)")
    print("=" * 55)
    print(f"  Total requests : {r['n']}")
    print(f"  Parallelism    : {r['workers']} threads")
    print(f"  Errors         : {r['errors']} ({r['error_rate']*100:.1f}%)")
    print(f"  Status codes   : {r['status_counts']}")
    print(f"  Latency (ms)")
    print(f"    min          : {r['min_ms']:.1f}")
    print(f"    median       : {r['median_ms']:.1f}")
    print(f"    P95          : {r['p95_ms']:.1f}   (target ≤ {P95_TARGET_MS})")
    print(f"    P99          : {r['p99_ms']:.1f}")
    print(f"    max          : {r['max_ms']:.1f}")
    if r["mem_delta_mb"] is not None:
        print(f"  Memory delta   : {r['mem_delta_mb']:+.1f} MB")
    print("=" * 55)
    passed = r["error_rate"] <= ERROR_RATE_MAX and r["p95_ms"] <= P95_TARGET_MS
    print(f"  HASIL AKHIR  : {'✅ LULUS' if passed else '❌ GAGAL'}")
    print("=" * 55 + "\n")
    return passed


# ── Pytest Automation Marker ──────────────────────────────────────────────────

@pytest.mark.stress
def test_stress_100_requests_local():
    """
    Memicu stress test otomatis via pytest runner ke port aktif 7860.
    """
    import httpx
    try:
        # 🌟 Diperbarui ke default port produksi terbaru 7860
        httpx.get("http://localhost:7860/health", timeout=2.0)
    except Exception:
        pytest.skip("Server tidak aktif di http://localhost:7860 — Lewati stress test.")

    result = run_stress_test(
        base_url="http://localhost:7860",
        api_key="changeme",
        n=N_REQUESTS,
        workers=MAX_WORKERS,
    )
    assert result["error_rate"] <= ERROR_RATE_MAX, f"Eror melebihi batas toleransi target!"
    assert result["p95_ms"] <= P95_TARGET_MS, f"Latensi P95 melambat melewati batas {P95_TARGET_MS}ms"


# ── CLI Entrypoint Runner ─────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ChatKasir API stress test")
    parser.add_argument("--url",     default="http://localhost:7860", help="Base URL API") # 🌟 Port default 7860
    parser.add_argument("--api-key", default="changeme",              help="API key")
    parser.add_argument("--n",       type=int, default=N_REQUESTS,    help="Jumlah total tembakan")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS,   help="Jumlah thread paralel")
    args = parser.parse_args()

    result  = run_stress_test(args.url, args.api_key, args.n, args.workers)
    passed  = print_results(result)
    sys.exit(0 if passed else 1)