import { useState, type FormEvent } from "react";

type CreateFormProps = {
  onCreate: (url: string) => Promise<void>;
  creating: boolean;
};

function normalizeUrl(raw: string): string {
  const trimmed = raw.trim();
  if (!trimmed) return trimmed;
  if (/^https?:\/\//i.test(trimmed)) return trimmed;
  return `https://${trimmed}`;
}

export function CreateForm({ onCreate, creating }: CreateFormProps) {
  const [url, setUrl] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    const normalized = normalizeUrl(url);
    if (!normalized) {
      setError("Enter a URL to shorten.");
      return;
    }

    try {
      new URL(normalized);
    } catch {
      setError("That doesn't look like a valid URL.");
      return;
    }

    try {
      await onCreate(normalized);
      setUrl("");
    } catch {
      // Parent surfaces toast; keep form values.
    }
  }

  return (
    <form className="create-form" onSubmit={(event) => void handleSubmit(event)}>
      <div className="create-row">
        <label className="sr-only" htmlFor="url">
          Long URL
        </label>
        <input
          id="url"
          name="url"
          type="text"
          inputMode="url"
          autoComplete="url"
          placeholder="https://example.com/very/long/path"
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          disabled={creating}
          required
        />
        <button type="submit" className="btn btn-primary" disabled={creating}>
          {creating ? "Shortening..." : "Shorten"}
        </button>
      </div>
      {error && <p className="field-error">{error}</p>}
    </form>
  );
}
