import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import { ArrowUp, Square, Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";

const MAX_CHARS = 2000;

interface Props {
  onSend: (text: string) => void;
  onClear: () => void;
  hasMessages: boolean;
  disabled?: boolean;
}

export function ChatInput({ onSend, onClear, hasMessages, disabled }: Props) {
  const [value, setValue] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 200) + "px";
  }, [value]);

  useEffect(() => {
    ref.current?.focus();
  }, []);

  const submit = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
    requestAnimationFrame(() => ref.current?.focus());
  };

  const onKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  const charCount = value.length;
  const nearLimit = charCount > MAX_CHARS * 0.8;

  return (
    <div className="sticky bottom-0 left-0 right-0 bg-gradient-to-t from-background via-background to-transparent pt-4 pb-4">
      <div className="mx-auto w-full max-w-[900px] px-4">
        <div className="flex items-end gap-3">
          {/* Clear button beside the text bar */}
          <button
            type="button"
            onClick={onClear}
            disabled={disabled || !hasMessages}
            title="Clear conversation"
            className={cn(
              "inline-flex h-[48px] w-[48px] shrink-0 items-center justify-center rounded-2xl border border-border bg-card text-muted-foreground transition-all cursor-pointer",
              "hover:bg-secondary hover:text-destructive hover:border-destructive/40",
              "disabled:opacity-30 disabled:hover:bg-card disabled:hover:text-muted-foreground disabled:cursor-not-allowed",
            )}
          >
            <Trash2 className="h-5 w-5" />
          </button>

          {/* Message input container */}
          <div className="relative flex-1 rounded-2xl border border-border bg-card shadow-lg focus-within:border-primary/60 transition-colors">
            <textarea
              ref={ref}
              value={value}
              onChange={(e) => setValue(e.target.value.slice(0, MAX_CHARS))}
              onKeyDown={onKey}
              rows={1}
              placeholder="Ask anything about your order..."
              aria-label="Message input"
              disabled={disabled}
              className="w-full resize-none bg-transparent px-4 py-3.5 pr-14 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none disabled:opacity-60"
            />
            <button
              type="button"
              onClick={submit}
              disabled={disabled || !value.trim()}
              aria-label={disabled ? "Sending" : "Send message"}
              className={cn(
                "absolute right-2 bottom-2 inline-flex h-9 w-9 items-center justify-center rounded-xl transition-all cursor-pointer",
                "bg-primary text-primary-foreground hover:opacity-90",
                "disabled:bg-muted disabled:text-muted-foreground disabled:cursor-not-allowed",
              )}
            >
              {disabled ? <Square className="h-4 w-4" /> : <ArrowUp className="h-4 w-4" />}
            </button>
          </div>
        </div>
        <div className="mt-2 flex items-center justify-between px-1 text-[11px] text-muted-foreground">
          <span>Press <kbd className="rounded bg-muted px-1.5 py-0.5">Enter</kbd> to send · <kbd className="rounded bg-muted px-1.5 py-0.5">Shift+Enter</kbd> newline</span>
          <span className={cn(nearLimit && "text-primary")}>{charCount}/{MAX_CHARS}</span>
        </div>
      </div>
    </div>
  );
}
