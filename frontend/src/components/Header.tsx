import type {} from "react";

type HeaderProps = {
  apiOk: boolean | null;
  onRefresh: () => void;
};

export function Header({ apiOk, onRefresh }: HeaderProps) {
  return (
    <header className="header">
      <div className="brand">
        <span className="brand-mark" aria-hidden="true">
          ⬡
        </span>
        <span className="brand-name">Shortink</span>
      </div>
      <div className="header-actions">
        <span className={`pill ${apiOk === null ? "" : apiOk ? "pill-ok" : "pill-bad"}`}>
          <span className="pill-dot" aria-hidden="true" />
          <span className="pill-label">
            <span className="pill-label-short">API</span>
            <span className="pill-label-full">API {apiOk === null ? "checking" : apiOk ? "online" : "offline"}</span>
          </span>
        </span>
        <button type="button" className="btn btn-ghost btn-refresh" onClick={onRefresh} aria-label="Refresh">
          <span className="btn-label-full">Refresh</span>
          <span className="btn-label-short" aria-hidden="true">
            ↻
          </span>
        </button>
      </div>
    </header>
  );
}
