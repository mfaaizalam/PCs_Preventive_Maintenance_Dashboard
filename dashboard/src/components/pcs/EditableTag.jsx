import { useEffect, useRef, useState } from "react";
import { Pencil, Check, X } from "lucide-react";

/**
 * A small "<icon> label <pencil>" tag used on PCCard for the fields an
 * admin can hand-correct (department, lab name, asset ID). Click the
 * pencil to swap the label for a text input; Enter/checkmark saves,
 * Escape/X cancels.
 *
 * PCCard itself is a react-router <Link> (clicking the card navigates
 * to the PC detail page), so every handler here calls
 * stopPropagation()/preventDefault() - otherwise tapping the pencil,
 * typing, or hitting save would also trigger card navigation.
 */
export default function EditableTag({ icon: Icon, value, placeholder, onSave, saving }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value || "");
  const inputRef = useRef(null);

  useEffect(() => {
    if (editing) inputRef.current?.focus();
  }, [editing]);

  useEffect(() => {
    if (!editing) setDraft(value || "");
  }, [value, editing]);

  const stop = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const startEdit = (e) => {
    stop(e);
    setDraft(value || "");
    setEditing(true);
  };

  const cancel = (e) => {
    stop(e);
    setEditing(false);
    setDraft(value || "");
  };

  const save = async (e) => {
    stop(e);
    const trimmed = draft.trim();
    if (trimmed && trimmed !== value) {
      await onSave(trimmed);
    }
    setEditing(false);
  };

  if (editing) {
    return (
      <span
        className="inline-flex items-center gap-1 rounded-md border border-brand-300 bg-white px-1.5 py-0.5"
        onClick={stop}
      >
        {Icon && <Icon className="h-3 w-3 shrink-0 text-ink-300" />}
        <input
          ref={inputRef}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onClick={stop}
          onKeyDown={(e) => {
            if (e.key === "Enter") save(e);
            if (e.key === "Escape") cancel(e);
          }}
          placeholder={placeholder}
          disabled={saving}
          className="w-20 min-w-0 border-none bg-transparent p-0 text-[12px] text-ink-800 focus:outline-none focus:ring-0"
        />
        <button
          type="button"
          onClick={save}
          disabled={saving}
          className="text-signal-healthy hover:opacity-70"
          aria-label="Save"
        >
          <Check className="h-3 w-3" />
        </button>
        <button type="button" onClick={cancel} className="text-ink-300 hover:opacity-70" aria-label="Cancel">
          <X className="h-3 w-3" />
        </button>
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1">
      {Icon && <Icon className="h-3 w-3 shrink-0" />}
      <span>{value || placeholder}</span>
      <button
        type="button"
        onClick={startEdit}
        className="text-ink-200 opacity-0 transition group-hover:opacity-100 hover:text-brand-500"
        aria-label={`Edit ${placeholder}`}
      >
        <Pencil className="h-2.5 w-2.5" />
      </button>
    </span>
  );
}