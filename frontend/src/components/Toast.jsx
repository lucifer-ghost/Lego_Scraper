import React from 'react';

export default function ToastContainer({ toasts, onDismiss }) {
  if (!toasts || toasts.length === 0) return null;

  return (
    <div className="toast-container" aria-live="polite">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`toast-alert toast-${t.type || 'success'}`}
          role="alert"
        >
          <div className="toast-icon-wrap">
            <span className="toast-icon">{t.icon || '✓'}</span>
          </div>

          <div className="toast-body">
            <div className="toast-header">
              <span className="toast-title">{t.title}</span>
              <button
                type="button"
                className="toast-close-btn"
                onClick={() => onDismiss(t.id)}
                aria-label="Dismiss alert"
              >
                ✕
              </button>
            </div>
            {t.message && <p className="toast-message">{t.message}</p>}
          </div>

          <div className="toast-progress-bar" />
        </div>
      ))}
    </div>
  );
}
