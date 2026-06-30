import type { ChatRequest, ChatResponse } from "@/types/chat";

const BASE_URL = (
  import.meta.env.VITE_API_URL || "https://brohud-customer-support.onrender.com"
).replace(/\/$/, "");

const TIMEOUT_MS = 30_000;

async function request<TRes>(
  path: string,
  init: RequestInit = {},
  timeoutMs: number = TIMEOUT_MS,
): Promise<TRes> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      ...init,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(init.headers ?? {}),
      },
    });

    if (!res.ok) {
      const text = await res.text().catch(() => "");
      throw new Error(`Server error ${res.status}: ${text || res.statusText}`);
    }

    return (await res.json()) as TRes;
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new Error("Request timed out. Please try again.");
    }

    if (err instanceof TypeError) {
      throw new Error("Network error. Check your connection and API URL.");
    }

    throw err;
  } finally {
    clearTimeout(timer);
  }
}

export const api = {
  async sendMessage(message: string): Promise<ChatResponse> {
    const body: ChatRequest = { message };

    return request<ChatResponse>("/chat", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  async trackOrder(orderId: string): Promise<ChatResponse> {
    return this.sendMessage(`Track my order ${orderId}`);
  },

  async recommendProducts(category: string, budget: number): Promise<ChatResponse> {
    return this.sendMessage(`Recommend a ${category} under ₹${budget}`);
  },

  async createSupportTicket(customerName: string, issue: string): Promise<ChatResponse> {
    return this.sendMessage(
      `Create a support ticket for ${customerName} regarding: ${issue}`,
    );
  },
};