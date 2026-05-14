"""
Stress test — kirim 100 request berturut-turut ke POST /predict.

Mengukur:
  - Median & P95 & P99 response time
  - Throughput (req/s)
  - Error rate (harus 0%)
  - Memory usage delta (sebelum vs sesudah)

Jalankan manual (bukan bagian CI otomatis):
    cd api-inference
    pip install httpx psutil --break-system-packages
    python tests/test_stress.py --url http://localhost:8000 --api-key changeme

Atau lewat pytest dengan marker khusus:
    pytest tests/test_stress.py -m stress -v
"""

from __future__ import annotations

import argparse
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest

# ── Payload ───────────────────────────────────────────────────────────────────

STRESS_PAYLOADS = [
    # Skenario 1: chat sederhana 1 produk
    "[07.42, 22/4/2026] Pembeli: bang 2 nasi goreng ya\n"
    "[07.44, 22/4/2026] Penjual: oke kak 1 nasi goreng 10rb totalnya 20rb ya",

    # Skenario 2: tanpa total
    "[08.00, 22/4/2026] Pembeli: pesan 3 es teh\n"
    "[08.01, 22/4/2026] Penjual: oke es teh 5rb ya",

    # Skenario 3: dengan slang
    "[07.42, 22/4/2026] Pembeli: bg psnnn nasgorrrr 2 yak\n"
    "[07.44, 22/4/2026] Penjual: oke kak 1 nasi goreng 10rb total 20rb",

    # Skenario 4: total tidak cocok
    "[09.00, 22/4/2026] Pembeli: mau 2 ayam bakar\n"
    "[09.01, 22/4/2026] Penjual: ayam bakar 15rb totalnya 25rb ya",

    # Skenario 5: harga tidak disebutkan
    "[10.00, 22/4/2026] Pembeli: pesan 1 jus alpukat\n"
    "[10.01, 22/4/2026] Penjual: oke, nanti saya cek harganya",
]

N_REQUESTS    = 100
MAX_WORKERS   = 10       # jumlah thread paralel
P95_TARGET_MS = 500.0    # target: P95 ≤ 500ms
ERROR_RATE_MAX = 0.0     # target: 0 error


# ── Core runner ───────────────────────────────────────────────────────────────

def _send_request(
    base_url: str,
    api_key: str,
    payload: str,
    session,
) -> tuple[int, float]:
    """
    Kirim satu POST /predict, kembalikan (status_code, elapsed_ms).
    Pakai httpx.Client (sync) agar mudah di-thread.
    """
    t0 = time.perf_counter()
    resp = session.post(
        f"{base_url}/predict",
        json={"raw_text": payload},
        headers={"X-API-Key": api_key},
        timeout=30.0,
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000
    return resp.status_code, elapsed_ms


def run_stress_test(
    base_url: str = "http://localhost:8000",
    api_key: str  = "changeme",
    n: int        = N_REQUESTS,
    workers: int  = MAX_WORKERS,
) -> dict:
    """
    Jalankan stress test, kembalikan dict hasil.
    """
    try:
        import httpx
    except ImportError:
        raise RuntimeError("httpx diperlukan: pip install httpx --break-system-packages")

    try:
        import psutil
        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
    except ImportError:
        mem_before = None

    results: list[tuple[int, float]] = []
    payloads = [STRESS_PAYLOADS[i % len(STRESS_PAYLOADS)] for i in range(n)]

    with httpx.Client() as session:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [
                executor.submit(_send_request, base_url, api_key, p, session)
                for p in payloads
            ]
            for fut in as_completed(futures):
                results.append(fut.result())

    status_codes = [r[0] for r in results]
    times_ms     = [r[1] for r in results]

    errors     = sum(1 for s in status_codes if s not in (200, 422))
    error_rate = errors / n

    sorted_times = sorted(times_ms)
    p50 = statistics.median(sorted_times)
    p95 = sorted_times[int(n * 0.95)]
    p99 = sorted_times[int(n * 0.99)]

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
        "min_ms":       min(times_ms),
        "max_ms":       max(times_ms),
        "median_ms":    p50,
        "p95_ms":       p95,
        "p99_ms":       p99,
        "mem_delta_mb": mem_delta,
        "status_counts": {str(s): status_codes.count(s) for s in set(status_codes)},
    }


def print_results(r: dict) -> None:
    print("\n" + "=" * 55)
    print("  STRESS TEST RESULTS — ChatKasir API-2")
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
    print(f"  HASIL: {'✅ LULUS' if passed else '❌ GAGAL'}")
    print("=" * 55 + "\n")
    return passed


# ── pytest marker (skip saat CI biasa) ───────────────────────────────────────

@pytest.mark.stress
def test_stress_100_requests_local():
    """
    Stress test 100 request ke localhost.
    Hanya dijalankan dengan: pytest -m stress

    Membutuhkan server berjalan di http://localhost:8000.
    Kalau server tidak aktif, test ini di-skip otomatis.
    """
    import httpx
    try:
        httpx.get("http://localhost:8000/health", timeout=2.0)
    except Exception:
        pytest.skip("Server tidak aktif di http://localhost:8000 — skip stress test")

    result = run_stress_test(
        base_url="http://localhost:8000",
        api_key="changeme",
        n=N_REQUESTS,
        workers=MAX_WORKERS,
    )
    assert result["error_rate"] <= ERROR_RATE_MAX, (
        f"Error rate {result['error_rate']*100:.1f}% melebihi target 0%"
    )
    assert result["p95_ms"] <= P95_TARGET_MS, (
        f"P95 latency {result['p95_ms']:.1f}ms melebihi target {P95_TARGET_MS}ms"
    )


# ── CLI runner ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ChatKasir API stress test")
    parser.add_argument("--url",     default="http://localhost:8000", help="Base URL API")
    parser.add_argument("--api-key", default="changeme",             help="API key")
    parser.add_argument("--n",       type=int, default=N_REQUESTS,   help="Jumlah request")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS,  help="Jumlah thread paralel")
    args = parser.parse_args()

    result  = run_stress_test(args.url, args.api_key, args.n, args.workers)
    passed  = print_results(result)
    sys.exit(0 if passed else 1)
