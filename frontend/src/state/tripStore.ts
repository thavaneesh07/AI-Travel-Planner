import { create } from "zustand";
import { listTrips, getTrip, deleteTrip, createTrip } from "../api/tripsApi";
import { Trip } from "../api/types";

interface TripState {
  savedTrips: any[];
  activeTrip: Trip | null;
  loading: boolean;
  error: string | null;

  fetchTrips: () => Promise<void>;
  fetchTripDetails: (tripid: number) => Promise<void>;
  deleteTripById: (tripid: number) => Promise<void>;
  saveTrip: (trip: Trip) => Promise<void>;
  clearActiveTrip: () => void;
}

export const useTripStore = create<TripState>((set) => ({
  savedTrips: [],
  activeTrip: null,
  loading: false,
  error: null,

  fetchTrips: async () => {
    set({ loading: true, error: null });
    try {
      const trips = await listTrips();
      set({ savedTrips: trips, loading: false });
    } catch (err) {
      set({ error: "Failed to load saved trips", loading: false });
    }
  },

  fetchTripDetails: async (tripid) => {
    set({ loading: true, error: null });
    try {
      const trip = await getTrip(tripid);
      set({ activeTrip: trip, loading: false });
    } catch (err) {
      set({ error: "Failed to load trip details", loading: false });
    }
  },

  deleteTripById: async (tripid) => {
    set({ loading: true, error: null });
    try {
      await deleteTrip(tripid);
      set((state) => ({
        savedTrips: state.savedTrips.filter((t) => t.id !== tripid),
        activeTrip: state.activeTrip?.tripid === tripid ? null : state.activeTrip,
        loading: false
      }));
    } catch (err) {
      set({ error: "Failed to delete trip", loading: false });
    }
  },

  saveTrip: async (trip) => {
    set({ loading: true, error: null });
    try {
      const res = await createTrip(trip);
      const trips = await listTrips();
      set({ savedTrips: trips, loading: false });
    } catch (err) {
      set({ error: "Failed to save trip", loading: false });
      throw err;
    }
  },

  clearActiveTrip: () => {
    set({ activeTrip: null });
  }
}));
