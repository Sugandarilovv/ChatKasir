/**
 * Format angka ke format Rupiah Indonesia
 * Contoh: formatRupiah(15000) => "Rp 15.000"
 */
export function formatRupiah(angka) {
  if (angka === null || angka === undefined) return 'Rp 0'
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
  }).format(angka)
}
