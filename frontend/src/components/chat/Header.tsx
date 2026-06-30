import { useState } from "react";
import { Menu, Settings as SettingsIcon, Info } from "lucide-react";
import logo from "@/assets/brohud-logo.png";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

interface Props {}

export function Header({}: Props) {
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [aboutOpen, setAboutOpen] = useState(false);
  const [sound, setSound] = useState(true);
  const [autoscroll, setAutoscroll] = useState(true);

  return (
    <>
      <header className="sticky top-0 z-20 flex h-14 items-center justify-between border-b border-border bg-background/80 px-3 backdrop-blur-md sm:px-5">
        <div className="flex min-w-0 items-center gap-3">
          <div className="flex min-w-0 items-center gap-3">
            <div className="h-7 shrink-0">
              <img src={logo} alt="Brohud" className="h-full w-auto object-contain" />
            </div>
            <div className="hidden h-5 w-px bg-border sm:block" />
            <div className="min-w-0">
              <h1 className="truncate font-display text-base font-normal uppercase tracking-widest sm:text-lg">
                AI Support
              </h1>
              <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-widest text-muted-foreground">
                <span className="relative flex h-1.5 w-1.5">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-emerald-500" />
                </span>
                Online · Powered by Lemma AI
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                aria-label="Menu"
                className="inline-flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground hover:bg-secondary hover:text-foreground cursor-pointer"
              >
                <Menu className="h-5 w-5" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-40">
              <DropdownMenuItem onClick={() => setSettingsOpen(true)} className="cursor-pointer">
                <SettingsIcon className="mr-2 h-4 w-4" />
                <span>Settings</span>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setAboutOpen(true)} className="cursor-pointer">
                <Info className="mr-2 h-4 w-4" />
                <span>About</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      <Dialog open={settingsOpen} onOpenChange={setSettingsOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Settings</DialogTitle>
            <DialogDescription>Customize your Brohud AI experience.</DialogDescription>
          </DialogHeader>
          <div className="space-y-5 py-2">
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="theme">Theme</Label>
                <p className="text-xs text-muted-foreground">Dark mode (default)</p>
              </div>
              <span className="rounded-full border border-border px-3 py-1 text-xs text-muted-foreground">Dark</span>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="autoscroll">Auto-scroll</Label>
                <p className="text-xs text-muted-foreground">Follow new messages as they arrive</p>
              </div>
              <Switch id="autoscroll" checked={autoscroll} onCheckedChange={setAutoscroll} />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="sound">Notification sound</Label>
                <p className="text-xs text-muted-foreground">Play a chime when responses arrive</p>
              </div>
              <Switch id="sound" checked={sound} onCheckedChange={setSound} />
            </div>
            <div className="rounded-lg border border-border bg-card/60 p-3 text-xs text-muted-foreground">
              API endpoint: <span className="font-mono text-foreground">{import.meta.env.NEXT_PUBLIC_API_URL ?? import.meta.env.VITE_API_URL ?? "http://localhost:8000"}</span>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={aboutOpen} onOpenChange={setAboutOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <div className="mb-3 h-10">
              <img src={logo} alt="Brohud" className="h-full w-auto object-contain" />
            </div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-primary">
              Est: 2024 · Drop IV
            </p>
            <DialogTitle className="font-display text-2xl font-normal uppercase tracking-widest">
              About Brohud
            </DialogTitle>
            <DialogDescription className="pt-1">
              Brohud is an independent streetwear label founded in 2024 — oversized silhouettes,
              signature script graphics, and limited drops. This AI Support concierge is the
              official customer help channel for orders, returns, sizing and drop info.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2 text-xs text-muted-foreground">
            <p>· Current drop: <span className="text-foreground">Drop IV</span></p>
            <p>· Shop: <a href="https://brohud.com" target="_blank" rel="noreferrer" className="text-primary hover:underline">brohud.com</a></p>
            <p>· Instagram: <a href="https://www.instagram.com/brohud.official" target="_blank" rel="noreferrer" className="text-primary hover:underline">@brohud.official</a></p>
            <p>· Powered by the Brohud AI runtime on Lemma Cloud.</p>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
