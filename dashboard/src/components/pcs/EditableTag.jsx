import { useEffect, useRef, useState } from "react";
import { Pencil, Check, X } from "lucide-react";

export default function EditableTag({
  icon: Icon,
  value,
  placeholder,
  onSave,
  saving,
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value || "");
  const inputRef = useRef(null);

  useEffect(() => {
    if (editing) {
      inputRef.current?.focus();
      inputRef.current?.select();
    }
  }, [editing]);

  useEffect(() => {
    if (!editing) {
      setDraft(value || "");
    }
  }, [value, editing]);

  const blockCard = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const startEdit = (e) => {
    blockCard(e);
    setDraft(value || "");
    setEditing(true);
  };

  const cancel = (e) => {
    blockCard(e);
    setEditing(false);
    setDraft(value || "");
  };

  const save = async (e) => {
    blockCard(e);

    const trimmed = draft.trim();

    if (!trimmed) {
      setEditing(false);
      setDraft(value || "");
      return;
    }

    if (trimmed !== value) {
      await onSave(trimmed);
    }

    setEditing(false);
  };

  if (editing) {
    return (
      <span
        className="inline-flex items-center gap-1"
        onPointerDown={blockCard}
        onClick={blockCard}
      >
        {Icon && (
          <Icon className="h-3.5 w-3.5 shrink-0 text-ink-400" />
        )}

        <input
          ref={inputRef}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onPointerDown={blockCard}
          onClick={blockCard}
          onKeyDown={(e) => {
            e.stopPropagation();

            if (e.key === "Enter") {
              save(e);
            }

            if (e.key === "Escape") {
              cancel(e);
            }
          }}
          placeholder={placeholder}
          disabled={saving}
          className="w-24 min-w-0 rounded border border-brand-300 bg-white px-1.5 py-0.5 text-[12px] font-medium text-ink-800 outline-none focus:border-brand-500 focus:outline-none focus:ring-0"
        />

        <button
          type="button"
          onPointerDown={blockCard}
          onClick={save}
          disabled={saving}
          className="inline-flex h-5 w-5 items-center justify-center rounded text-signal-healthy transition-colors hover:bg-signal-healthy/10 disabled:opacity-50"
          aria-label="Save"
          title="Save"
        >
          <Check className="h-3.5 w-3.5" strokeWidth={2.5} />
        </button>

        <button
          type="button"
          onPointerDown={blockCard}
          onClick={cancel}
          disabled={saving}
          className="inline-flex h-5 w-5 items-center justify-center rounded text-ink-400 transition-colors hover:bg-ink-100 disabled:opacity-50"
          aria-label="Cancel"
          title="Cancel"
        >
          <X className="h-3.5 w-3.5" strokeWidth={2.5} />
        </button>
      </span>
    );
  }

  return (
    <span
      className="inline-flex items-center gap-1.5"
      onPointerDown={blockCard}
      onClick={blockCard}
    >
      {Icon && (
        <Icon className="h-3.5 w-3.5 shrink-0 text-ink-400" />
      )}

      <span className="font-medium text-ink-500">
        {value || placeholder}
      </span>

      <button
        type="button"
        onPointerDown={blockCard}
        onClick={startEdit}
        className="ml-0.5 inline-flex h-5 w-5 items-center justify-center rounded text-ink-300 transition-colors hover:bg-brand-50 hover:text-brand-600"
        aria-label={`Edit ${placeholder}`}
        title={`Edit ${placeholder}`}
      >
        <Pencil className="h-3 w-3" strokeWidth={2} />
      </button>
    </span>
  );
}
