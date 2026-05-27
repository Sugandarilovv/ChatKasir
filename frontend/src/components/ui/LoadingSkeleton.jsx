/**
 * Skeleton loading untuk tabel transaksi
 * Props: rows - jumlah baris skeleton (default 5)
 */
export default function LoadingSkeleton({ rows = 5 }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4 items-center p-3 bg-base-100 rounded-lg">
          <div className="skeleton h-4 w-1/3" />
          <div className="skeleton h-4 w-16" />
          <div className="skeleton h-4 w-24" />
          <div className="skeleton h-4 w-24" />
        </div>
      ))}
    </div>
  )
}
