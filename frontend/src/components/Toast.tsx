type ToastProps = {
  message: string;
  tone: "success" | "error" | "info";
  onClose: () => void;
};

export function Toast({ message, tone, onClose }: ToastProps) {
  return (
    <div className={`toast toast-${tone}`} role="status">
      <span>{message}</span>
      <button type="button" className="toast-close" onClick={onClose} aria-label="Dismiss">
        ×
      </button>
    </div>
  );
}
