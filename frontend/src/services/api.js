import axios from "axios";

// ✅ Base URL of your FastAPI backend
const API_BASE_URL = "http://127.0.0.1:8000/api";

/**
 * Parse a user message into structured trip data
 * @param {string} message - The user's chat input
 */
export async function parseMessage(message) {
  const res = await axios.post(`${API_BASE_URL}/parse`, { message });
  return res.data;
}

/**
 * Generate an itinerary from structured data
 * @param {object} data - The parsed trip info (destination, dates, etc.)
 */
export async function generateItinerary(data) {
  const res = await axios.post(`${API_BASE_URL}/itineraries`, data);
  return res.data;
}

/**
 * Fetch weather data for a city
 * @param {string} city - The destination city
 */
export async function getWeather(city) {
  const res = await axios.get(`${API_BASE_URL}/weather/${city}`);
  return res.data;
}

/**
 * 🔹 NEW — Combined endpoint that does NLP + itinerary + weather in one step
 * @param {string} message - Natural language trip request
 */
export async function planTrip(message) {
  const res = await axios.post(`${API_BASE_URL}/plan`, { message });
  return res.data;
}

/**
 * Get smart AI travel suggestions
 * @param {object} tripData - Full trip data (parsed query + itinerary)
 */
export const getSuggestions = async (tripData) => {
  const body = {
    destination: tripData?.parsed_query?.destination || "",
    budget: parseFloat(tripData?.parsed_query?.budget || 0),
    total_estimated_cost: parseFloat(
      tripData?.generated_itinerary?.total_estimated_cost || 0
    ),
    interests: tripData?.parsed_query?.interests || [],
    weather_forecast:
      tripData?.generated_itinerary?.days?.map(
        (d) => d.weather?.desc || ""
      ) || [],
  };

  const res = await fetch("http://127.0.0.1:8000/api/suggestions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) throw new Error("Failed to fetch suggestions");
  return await res.json();
};

export async function getHotels(data) {
  try {
    const res = await fetch("http://localhost:8000/api/hotels", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        destination: data.parsed_query.destination,
        budget: data.parsed_query.budget,
        interests: data.parsed_query.interests
      })
    });

    if (!res.ok) {
      console.error("Hotels API failed:", res.status);
      return { hotels: [] };
    }

    return await res.json();
  } catch (err) {
    console.error("HOTELS FETCH ERROR:", err);
    return { hotels: [] };
  }
}
