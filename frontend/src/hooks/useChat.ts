import { useCallback, useRef, useState } from "react";
import { toast } from "sonner";
import { api } from "@/services/api";
import type { Message } from "@/types/chat";

function uid() {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const lastUserMessageRef = useRef<string | null>(null);

  const send = useCallback(async (raw: string) => {
    const content = raw.trim();
    if (!content || loading) return;

    const userMsg: Message = {
      id: uid(),
      role: "user",
      content,
      timestamp: Date.now(),
    };
    lastUserMessageRef.current = content;
    setMessages((m) => [...m, userMsg]);
    setLoading(true);
    setError(null);

    try {
      const res = await api.sendMessage(content);
      const assistantMsg: Message = {
        id: uid(),
        role: "assistant",
        content: res.response ?? "(no response)",
        timestamp: Date.now(),
        source: res.source,
      };
      setMessages((m) => [...m, assistantMsg]);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Something went wrong";
      setError(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  }, [loading]);

  const retry = useCallback(() => {
    if (lastUserMessageRef.current) void send(lastUserMessageRef.current);
  }, [send]);

  const clear = useCallback(() => {
    setMessages([]);
    setError(null);
    lastUserMessageRef.current = null;
  }, []);

  return { messages, loading, error, send, retry, clear };
}
