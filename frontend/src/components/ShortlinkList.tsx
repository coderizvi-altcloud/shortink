import { useState } from "react";
import type { Shortlink } from "../types";
import { ShortlinkRow } from "./ShortlinkRow";

type ShortlinkListProps = {
  items: Shortlink[];
  loading: boolean;
  onCopy: (text: string) => void;
  onUpdate: (id: number, payload: { url?: string; short_code?: string }) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
};

export function ShortlinkList({ items, loading, onCopy, onUpdate, onDelete }: ShortlinkListProps) {
  const [editingId, setEditingId] = useState<number | null>(null);

  if (loading) {
    return (
      <div className="empty-state" role="status">
        <div className="skeleton-stack">
          <div className="skeleton" />
          <div className="skeleton" />
          <div className="skeleton" />
        </div>
        <p className="muted">Loading shortlinks...</p>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon" aria-hidden="true">
          ↗
        </div>
        <h3>No shortlinks yet</h3>
        <p className="muted">Create your first one above - it only takes a URL.</p>
      </div>
    );
  }

  return (
    <ul className="shortlink-list">
      {items.map((item) => (
        <ShortlinkRow
          key={item.id}
          item={item}
          editing={editingId === item.id}
          onStartEdit={() => setEditingId(item.id)}
          onCancelEdit={() => setEditingId(null)}
          onCopy={onCopy}
          onUpdate={async (payload) => {
            await onUpdate(item.id, payload);
            setEditingId(null);
          }}
          onDelete={() => onDelete(item.id)}
        />
      ))}
    </ul>
  );
}
