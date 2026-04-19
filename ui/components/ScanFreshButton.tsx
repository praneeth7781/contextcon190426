"use client";

interface ScanFreshButtonProps {
  onClick: () => void;
  isScanning: boolean;
}

export function ScanFreshButton({ onClick, isScanning }: ScanFreshButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={isScanning}
      className="fixed bottom-6 right-6 px-4 py-2 bg-accent-primary text-white rounded-lg shadow-lg hover:bg-accent-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-sm font-medium"
    >
      {isScanning ? "Scanning..." : "Scan fresh"}
    </button>
  );
}
