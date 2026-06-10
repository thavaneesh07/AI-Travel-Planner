import { create } from "zustand";
import { generate, chatEdit, updateDay } from "../api/generateApi";
import { Trip, GenerateResponse } from "../api/types";

interface ChatMessage {
  role: "user" | "assistant";
  text: string;
}

interface PlanningState {
  messages: ChatMessage[];
  sessionid: string | null;
  planningstate: any;
  missingfields: string[];
  currentQuestion: string | null;
  tripData: Trip | null;
  loading: boolean;
  error: string | null;
  
  sendMessage: (message: string) => Promise<void>;
  editTrip: (tripid: number, message: string) => Promise<void>;
  updateDayActivities: (tripid: number, day: number, activities: any[]) => Promise<void>;
  setTripData: (trip: Trip | null) => void;
  resetPlanning: () => void;
}

export const usePlanningStore = create<PlanningState>((set, get) => ({
  messages: [
    { role: "assistant", text: "Hi! 👋 I'm your AI travel assistant. How can I help today?" }
  ],
  sessionid: null,
  planningstate: { entities: {} },
  missingfields: [],
  currentQuestion: null,
  tripData: null,
  loading: false,
  error: null,

  sendMessage: async (text: string) => {
    const userMsg: ChatMessage = { role: "user", text };
    set((state) => ({
      messages: [...state.messages, userMsg],
      loading: true,
      error: null
    }));

    try {
      const state = get();
      const history = state.messages.map((m) => ({ role: m.role, text: m.text }));
      const res: GenerateResponse = await generate(
        text,
        state.sessionid || undefined,
        state.planningstate,
        history,
        state.tripData || undefined,
        state.tripData?.tripid || undefined
      );

      if (res.status === "needsmoreinfo") {
        set((state) => ({
          sessionid: res.sessionid || state.sessionid,
          planningstate: res.planningstate || state.planningstate,
          missingfields: res.missingfields || [],
          currentQuestion: res.question || null,
          messages: [
            ...state.messages,
            { role: "assistant", text: res.question || "Could you tell me more?" }
          ],
          loading: false
        }));
      } else if (res.status === "success") {
        if (res.intent === "travelquestion" || res.intent === "nontravel") {
          set((state) => ({
            messages: [
              ...state.messages,
              { role: "assistant", text: res.answer || "Here is what I found." }
            ],
            loading: false
          }));
        } else if ((res.intent === "plantrip" || res.intent === "modifytrip" || res.intent === "modify_trip") && res.trip) {
          const isPlantrip = res.intent === "plantrip";
          set((state) => ({
            tripData: { ...res.trip!, tripid: res.tripid || state.tripData?.tripid || null, budget: res.budget || state.tripData?.budget },
            messages: [
              ...state.messages,
              { role: "assistant", text: res.answer || (isPlantrip ? "🎉 I have generated a custom trip itinerary for you!" : "🎉 I have updated your trip itinerary!") }
            ],
            loading: false
          }));
        }
      } else {
        set((state) => ({
          messages: [
            ...state.messages,
            { role: "assistant", text: "I encountered an issue processing your query." }
          ],
          loading: false
        }));
      }
    } catch (err: any) {
      set((state) => ({
        error: "Server connection failed",
        messages: [
          ...state.messages,
          { role: "assistant", text: "❌ Connection error. Please try again." }
        ],
        loading: false
      }));
    }
  },

  editTrip: async (tripid: number, message: string) => {
    const userMsg: ChatMessage = { role: "user", text: message };
    set((state) => ({
      messages: [...state.messages, userMsg],
      loading: true,
      error: null
    }));

    try {
      const res = await chatEdit(tripid, message);
      if (res.status === "success" && res.trip) {
        set((state) => ({
          tripData: res.trip,
          messages: [
            ...state.messages,
            { role: "assistant", text: `I have updated your itinerary based on: "${message}"` }
          ],
          loading: false
        }));
      } else {
        set((state) => ({
          messages: [
            ...state.messages,
            { role: "assistant", text: "I couldn't modify the itinerary with that instruction." }
          ],
          loading: false
        }));
      }
    } catch (err) {
      set((state) => ({
        messages: [
          ...state.messages,
          { role: "assistant", text: "❌ Editing error. Please try again." }
        ],
        loading: false
      }));
    }
  },

  updateDayActivities: async (tripid: number, day: number, activities: any[]) => {
    set({ loading: true, error: null });
    try {
      const res = await updateDay(tripid, day, activities);
      if (res.status === "success" && res.trip) {
        set({ tripData: res.trip, loading: false });
      } else {
        set({ error: "Failed to update day activities", loading: false });
      }
    } catch (err) {
      set({ error: "Connection error", loading: false });
    }
  },

  setTripData: (trip) => {
    set({ tripData: trip });
  },

  resetPlanning: () => {
    set({
      messages: [
        { role: "assistant", text: "Hi! 👋 I'm your AI travel assistant. How can I help today?" }
      ],
      sessionid: null,
      planningstate: { entities: {} },
      missingfields: [],
      currentQuestion: null,
      tripData: null,
      loading: false,
      error: null
    });
  }
}));
