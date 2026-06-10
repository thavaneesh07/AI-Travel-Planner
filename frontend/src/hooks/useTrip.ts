import { useTripStore } from "../state/tripStore";

export const useTrip = () => {
  const store = useTripStore();
  return {
    savedTrips: store.savedTrips,
    activeTrip: store.activeTrip,
    loading: store.loading,
    error: store.error,
    fetchTrips: store.fetchTrips,
    fetchTripDetails: store.fetchTripDetails,
    deleteTripById: store.deleteTripById,
    clearActiveTrip: store.clearActiveTrip,
    saveTrip: store.saveTrip
  };
};
