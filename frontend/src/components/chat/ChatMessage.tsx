import { memo, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Check, Copy } from "lucide-react";
import type { Message } from "@/types/chat";
import { cn } from "@/lib/utils";

function formatTime(ts: number) {
  return new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function ChatMessageBase({ message }: { message: Message }) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === "user";

  const copy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className={cn("fade-in flex w-full gap-2", isUser ? "justify-end" : "justify-start")}>
      <div className={cn("group flex flex-col max-w-[85%] sm:max-w-[75%]", isUser ? "items-end" : "items-start")}>
        <div
          className={cn(
            "px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm",
            isUser
              ? "bg-bubble-user text-bubble-user-foreground rounded-br-sm"
              : "bg-bubble-assistant text-bubble-assistant-foreground rounded-bl-sm",
          )}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="markdown">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>
        <div className="mt-1 flex items-center gap-2 px-1 text-[11px] text-muted-foreground">
          <span>{formatTime(message.timestamp)}</span>
          {message.source && <span className="opacity-70">· {message.source}</span>}
          {!isUser && (
            <button
              onClick={copy}
              aria-label="Copy message"
              className="opacity-0 group-hover:opacity-100 transition-opacity inline-flex items-center gap-1 hover:text-foreground"
            >
              {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
              {copied ? "Copied" : "Copy"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export const ChatMessage = memo(ChatMessageBase);
