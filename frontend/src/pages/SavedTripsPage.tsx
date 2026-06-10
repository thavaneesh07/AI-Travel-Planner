import React, { useEffect } from "react";
import { useTrip } from "../hooks/useTrip";
import { useTripStore } from "../state/tripStore";
import { usePlanning } from "../hooks/usePlanning";

interface SavedTripsPageProps {
  onBackToPlanner: () => void;
}

export const SavedTripsPage: React.FC<SavedTripsPageProps> = ({ onBackToPlanner }) => {
  const { savedTrips, fetchTrips, deleteTripById, fetchTripDetails, loading } = useTrip();
  const { setTripData } = usePlanning();

  useEffect(() => {
    fetchTrips();
  }, []);

  const handleViewDetails = async (id: number) => {
    await fetchTripDetails(id);
    const trip = useTripStore.getState().activeTrip;
    if (trip) {
      setTripData(trip);
      onBackToPlanner();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-3xl font-extrabold text-gray-800">Your Saved Journeys</h2>
          <button
            onClick={onBackToPlanner}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl transition-all shadow-md"
          >
            ← Back to Planner
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12 text-gray-500 font-medium">Loading saved trips...</div>
        ) : savedTrips.length === 0 ? (
          <div className="bg-white p-8 rounded-3xl text-center shadow-sm border border-gray-100 text-gray-500 font-medium py-12">
            No saved trips found. Plan your first journey and save it!
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {savedTrips.map((trip) => (
              <div key={trip.id} className="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm hover:shadow-md transition-all duration-300 flex flex-col justify-between space-y-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-800">🌸 {trip.destination}</h3>
                  <p className="text-xs text-gray-400 mt-1">{trip.country || "N/A"}</p>
                  <p className="text-sm text-gray-650 mt-3 font-medium">
                    📅 {trip.startdate} to {trip.enddate}
                  </p>
                  <p className="text-sm font-semibold text-green-600 mt-1">
                    💰 Budget: {trip.currency || "USD"} {trip.budget}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleViewDetails(trip.id)}
                    className="flex-1 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold rounded-xl transition-all"
                  >
                    View Details
                  </button>
                  <button
                    onClick={() => deleteTripById(trip.id)}
                    className="px-4 py-2 bg-red-50 hover:bg-red-100 text-red-700 font-bold rounded-xl transition-all"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
