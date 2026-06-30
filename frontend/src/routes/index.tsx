import { createFileRoute } from "@tanstack/react-router";
import { Toaster } from "@/components/ui/sonner";
import { Header } from "@/components/chat/Header";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { ChatInput } from "@/components/chat/ChatInput";
import { useChat } from "@/hooks/useChat";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Brohud AI Customer Support" },
      { name: "description", content: "Brohud AI — premium streetwear customer support. Track orders, get product picks, and resolve issues instantly." },
      { property: "og:title", content: "Brohud AI Customer Support" },
      { property: "og:description", content: "Premium streetwear AI concierge for orders, returns, and recommendations." },
    ],
  }),
  component: Index,
});

function Index() {
  const { messages, loading, send, clear } = useChat();

  return (
    <div className="flex h-svh w-full overflow-hidden bg-background text-foreground">
      <main className="flex min-w-0 flex-1 flex-col">
        <Header />

        <div className="flex flex-1 flex-col overflow-y-auto">
          <ChatWindow messages={messages} loading={loading} onPick={send} />
        </div>

        <ChatInput
          onSend={send}
          onClear={clear}
          hasMessages={messages.length > 0}
          disabled={loading}
        />
      </main>

      <Toaster theme="dark" position="top-center" richColors />
    </div>
  );
}
