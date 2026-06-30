import { Package, RefreshCcw, Undo2, Truck, Sparkle, LifeBuoy, type LucideIcon } from "lucide-react";
import logo from "@/assets/brohud-logo.png";

interface Topic {
  icon: LucideIcon;
  label: string;
  prompt: string;
}

const TOPICS: Topic[] = [
  { icon: Truck, label: "Shipping", prompt: "How long does shipping take?" },
  { icon: RefreshCcw, label: "Refund", prompt: "What is your refund policy?" },
  { icon: Undo2, label: "Returns", prompt: "What is your return policy?" },
  { icon: Package, label: "Track Order", prompt: "Track my order BH1001" },
  { icon: Sparkle, label: "Style Match", prompt: "Recommend a hoodie under ₹2000" },
  { icon: LifeBuoy, label: "Support", prompt: "I received a damaged product." },
];

const SUGGESTIONS = [
  "Track my order BH1001",
  "How long does shipping take?",
  "What is your refund policy?",
  "Recommend a hoodie under ₹2000",
];

export function EmptyState({ onPick }: { onPick: (text: string) => void }) {
  return (
    <div className="fade-in mx-auto flex w-full max-w-[820px] flex-col items-center px-4 py-10 text-center">
      <div className="mb-6 h-16 w-auto px-2">
        <img src={logo} alt="Brohud" className="h-full w-auto object-contain" />
      </div>
      <p className="mb-2 text-[10px] font-semibold uppercase tracking-[0.3em] text-primary">
        Est: 2024 · Drop IV Live
      </p>
      <h1 className="font-display text-4xl font-normal uppercase tracking-wider sm:text-5xl">
        Welcome to <span className="text-primary">Brohud</span> Support
      </h1>
      <p className="mt-3 max-w-lg text-sm text-muted-foreground">
        Official AI concierge for the Brohud streetwear line. Tracking, drops, fit advice — handled.
      </p>

      <div className="mt-8 grid w-full grid-cols-2 gap-2 sm:grid-cols-3">
        {TOPICS.map(({ icon: Icon, label, prompt }) => (
          <button
            key={label}
            type="button"
            onClick={() => onPick(prompt)}
            aria-label={`Start chat about ${label}`}
            className="group flex items-center gap-2 rounded-xl border border-border bg-card/60 px-3 py-2.5 text-left text-xs text-muted-foreground transition-all hover:border-primary hover:bg-primary/10 hover:text-foreground"
          >
            <Icon className="h-4 w-4 text-primary transition-transform group-hover:scale-110" />
            <span>{label}</span>
          </button>
        ))}
      </div>

      <div className="mt-8 w-full">
        <p className="mb-3 text-xs uppercase tracking-widest text-muted-foreground">Try asking</p>
        <div className="flex flex-wrap justify-center gap-2">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => onPick(s)}
              className="rounded-full border border-border bg-card px-4 py-2 text-sm text-foreground transition-all hover:border-primary hover:bg-primary/10 hover:text-primary"
            >
              {s}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
