// src/services/api.js
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
