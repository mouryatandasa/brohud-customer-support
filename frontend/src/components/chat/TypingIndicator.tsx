export function TypingIndicator() {
  return (
    <div className="flex items-center gap-1.5 px-4 py-3 rounded-2xl bg-bubble-assistant w-fit">
      <span className="bounce-dot h-2 w-2 rounded-full bg-muted-foreground" style={{ animationDelay: "0s" }} />
      <span className="bounce-dot h-2 w-2 rounded-full bg-muted-foreground" style={{ animationDelay: "0.15s" }} />
      <span className="bounce-dot h-2 w-2 rounded-full bg-muted-foreground" style={{ animationDelay: "0.3s" }} />
    </div>
  );
}
