/**
 * Tampilan kosong ketika tidak ada data
 * Props:
 *   message - pesan utama
 *   action  - { label, onClick } tombol aksi opsional
 */
export default function EmptyState({ message = 'Belum ada data.', action }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <span style={{ fontSize: 48 }}>📭</span>
      <p className="mt-4 text-base-content/60 text-sm">{message}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="btn btn-primary btn-sm mt-4"
        >
          {action.label}
        </button>
      )}
    </div>
  )
}
