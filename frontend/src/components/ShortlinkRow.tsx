import { useState, type FormEvent } from "react";
import type { Shortlink } from "../types";

type ShortlinkRowProps = {
  item: Shortlink;
  editing: boolean;
  onStartEdit: () => void;
  onCancelEdit: () => void;
  onCopy: (text: string) => void;
  onUpdate: (payload: { url?: string; short_code?: string }) => Promise<void>;
  onDelete: () => void;
};

export function ShortlinkRow({
  item,
  editing,
  onStartEdit,
  onCancelEdit,
  onCopy,
  onUpdate,
  onDelete,
}: ShortlinkRowProps) {
  const [url, setUrl] = useState(item.url);
  const [shortCode, setShortCode] = useState(item.short_code);
  const [saving, setSaving] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);

  async function handleSave(event: FormEvent) {
    event.preventDefault();
    const payload: { url?: string; short_code?: string } = {};
    if (url.trim() && url.trim() !== item.url) payload.url = url.trim();
    if (shortCode.trim() && shortCode.trim() !== item.short_code) {
      payload.short_code = shortCode.trim();
    }
    if (!payload.url && !payload.short_code) {
      onCancelEdit();
      return;
    }

    setSaving(true);
    try {
      await onUpdate(payload);
    } finally {
      setSaving(false);
    }
  }

  if (editing) {
    return (
      <li className="shortlink-card editing">
        <form className="edit-form" onSubmit={(event) => void handleSave(event)}>
          <label>
            <span>Destination URL</span>
            <input value={url} onChange={(event) => setUrl(event.target.value)} required />
          </label>
          <label>
            <span>Short code</span>
            <input
              value={shortCode}
              onChange={(event) => setShortCode(event.target.value)}
              pattern="[A-Za-z0-9_-]+"
              title="Letters, numbers, underscores, hyphens"
              required
            />
          </label>
          <div className="row-actions">
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? "Saving..." : "Save"}
            </button>
            <button
              type="button"
              className="btn btn-ghost"
              onClick={() => {
                setUrl(item.url);
                setShortCode(item.short_code);
                onCancelEdit();
              }}
              disabled={saving}
            >
              Cancel
            </button>
          </div>
        </form>
      </li>
    );
  }

  return (
    <li className="shortlink-card">
      <div className="card-main">
        <div className="card-title-row">
          <a className="short-url" href={item.short_url} target="_blank" rel="noreferrer">
            {item.short_url}
          </a>
          <span className="click-badge" title="Click count">
            {item.click_count} click{item.click_count === 1 ? "" : "s"}
          </span>
        </div>
        <p className="dest-url" title={item.url}>
          {item.url}
        </p>
        <p className="meta">
          <span className="mono">#{item.id}</span>
          <span className="dot" aria-hidden="true">
            ·
          </span>
          <span className="mono">/{item.short_code}</span>
        </p>
      </div>
      <div className="row-actions">
        <button type="button" className="btn btn-secondary" onClick={() => onCopy(item.short_url)}>
          Copy
        </button>
        <button
          type="button"
          className="btn btn-ghost"
          onClick={() => {
            setUrl(item.url);
            setShortCode(item.short_code);
            setConfirmDelete(false);
            onStartEdit();
          }}
        >
          Edit
        </button>
        {confirmDelete ? (
          <>
            <button type="button" className="btn btn-danger" onClick={onDelete}>
              Confirm
            </button>
            <button type="button" className="btn btn-ghost" onClick={() => setConfirmDelete(false)}>
              Keep
            </button>
          </>
        ) : (
          <button type="button" className="btn btn-ghost danger-text" onClick={() => setConfirmDelete(true)}>
            Delete
          </button>
        )}
      </div>
    </li>
  );
}
