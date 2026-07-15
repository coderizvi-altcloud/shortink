import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";
import { api, HOSTED_API_BASE } from "./api";
import type { Shortlink } from "./types";
import { CreateForm } from "./components/CreateForm";
import { ShortlinkList } from "./components/ShortlinkList";
import { Toast } from "./components/Toast";
import { Header } from "./components/Header";

type ToastTone = "success" | "error" | "info";

type ToastState = {
  message: string;
  tone: ToastTone;
} | null;

export default function App() {
  const [shortlinks, setShortlinks] = useState<Shortlink[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [apiOk, setApiOk] = useState<boolean | null>(null);
  const [toast, setToast] = useState<ToastState>(null);
  const [query, setQuery] = useState("");

  const showToast = useCallback((message: string, tone: ToastTone = "info") => {
    setToast({ message, tone });
  }, []);

  const load = useCallback(async () => {
    try {
      const [items, health] = await Promise.all([
        api.listShortlinks(),
        api.health().catch(() => null),
      ]);
      setShortlinks(items);
      setApiOk(health?.ok ?? true);
    } catch (err) {
      setApiOk(false);
      showToast(err instanceof Error ? err.message : "Failed to load shortlinks", "error");
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (!toast) return;
    const timer = window.setTimeout(() => setToast(null), 3200);
    return () => window.clearTimeout(timer);
  }, [toast]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return shortlinks;
    return shortlinks.filter(
      (item) =>
        item.url.toLowerCase().includes(q) ||
        item.short_code.toLowerCase().includes(q) ||
        item.short_url.toLowerCase().includes(q),
    );
  }, [query, shortlinks]);

  async function handleCreate(url: string) {
    setCreating(true);
    try {
      const created = await api.createShortlink({ url });
      setShortlinks((prev) => {
        const without = prev.filter((item) => item.id !== created.id);
        return [created, ...without];
      });
      showToast("Shortlink created", "success");
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Failed to create shortlink", "error");
      throw err;
    } finally {
      setCreating(false);
    }
  }

  async function handleUpdate(id: number, payload: { url?: string; short_code?: string }) {
    try {
      const updated = await api.updateShortlink(id, payload);
      setShortlinks((prev) => prev.map((item) => (item.id === id ? updated : item)));
      showToast("Shortlink updated", "success");
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Failed to update shortlink", "error");
      throw err;
    }
  }

  async function handleDelete(id: number) {
    try {
      await api.deleteShortlink(id);
      setShortlinks((prev) => prev.filter((item) => item.id !== id));
      showToast("Shortlink deleted", "success");
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Failed to delete shortlink", "error");
    }
  }

  async function handleCopy(text: string) {
    try {
      await navigator.clipboard.writeText(text);
      showToast("Copied to clipboard", "success");
    } catch {
      showToast("Could not copy â€” select and copy manually", "error");
    }
  }

  function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
  }

  return (
    <div className="app">
      <div className="bg-glow" aria-hidden="true" />
      <Header apiOk={apiOk} onRefresh={() => void load()} />

      <main className="main">
        <section className="hero">
          <p className="eyebrow">URL shortener</p>
          <h1>
            Shorten links.
            <span className="hero-accent"> Track every click.</span>
          </h1>
          <p className="hero-sub">
            Paste a long URL, get a compact short code, and manage everything from one clean dashboard.
          </p>
          <CreateForm onCreate={handleCreate} creating={creating} />
        </section>

        <section className="list-section">
          <div className="list-header">
            <div>
              <h2>Your shortlinks</h2>
              <p className="muted">Edit destinations, customize codes, or remove links you no longer need.</p>
            </div>
            <form className="search" onSubmit={handleSearch}>
              <label className="sr-only" htmlFor="search">
                Search shortlinks
              </label>
              <input
                id="search"
                type="search"
                placeholder="Search by URL or codeâ€¦"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
            </form>
          </div>

          <ShortlinkList
            items={filtered}
            loading={loading}
            onCopy={handleCopy}
            onUpdate={handleUpdate}
            onDelete={handleDelete}
          />
        </section>
      </main>

      <footer className="footer">
        <span>Shortink</span>
        <a href={`${HOSTED_API_BASE}/docs`} target="_blank" rel="noreferrer">
          API docs
        </a>
      </footer>

      {toast && <Toast message={toast.message} tone={toast.tone} onClose={() => setToast(null)} />}
    </div>
  );
}
