import { useEffect, useRef } from "react";
import type { Message } from "@/types/chat";
import { ChatMessage } from "./ChatMessage";
import { TypingIndicator } from "./TypingIndicator";
import { EmptyState } from "./EmptyState";

interface Props {
  messages: Message[];
  loading: boolean;
  onPick: (text: string) => void;
}

export function ChatWindow({ messages, loading, onPick }: Props) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  if (messages.length === 0 && !loading) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <EmptyState onPick={onPick} />
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-[900px] flex-1 px-4 py-6">
      <div className="flex flex-col gap-5">
        {messages.map((m) => (
          <ChatMessage key={m.id} message={m} />
        ))}
        {loading && (
          <div className="fade-in flex justify-start">
            <TypingIndicator />
          </div>
        )}
        <div ref={endRef} />
      </div>
    </div>
  );
}
