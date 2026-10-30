import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [location, setLocation] = useState("Bengaluru");
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function checkWeather(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setForecast(null);

    try {
      const response = await fetch(`${API_URL}/api/weather`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ location }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to fetch forecast.");
      }

      setForecast(data);
    } catch (err) {
      setError(err.message || "Could not connect to the backend.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <h1>Weather & Calendar Assistant</h1>
      <p>Check the forecast before planning your next event.</p>

      <form onSubmit={checkWeather}>
        <label htmlFor="location">Event location</label>

        <input
          id="location"
          value={location}
          onChange={(event) => setLocation(event.target.value)}
          placeholder="Enter a city"
          required
        />

        <button disabled={loading}>
          {loading ? "Checking..." : "Check Weather"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {forecast && (
        <section className="forecast">
          <h2>
            {forecast.location}
            {forecast.country ? `, ${forecast.country}` : ""}
          </h2>

          <p>Timezone: {forecast.timezone}</p>

          <h3>Next available forecast hour</h3>

          <p>
            Time: {forecast.hourly.time[0]}
          </p>

          <p>
            Temperature: {forecast.hourly.temperature_2m[0]} °C
          </p>

          <p>
            Rain probability:{" "}
            {forecast.hourly.precipitation_probability[0] ?? "N/A"}%
          </p>

          <p>
            Precipitation:{" "}
            {forecast.hourly.precipitation[0] ?? "N/A"} mm
          </p>

          <p className="note">
            This is the first available forecast hour, not necessarily
            the time of your planned event.
          </p>
        </section>
      )}
    </main>
  );
}

export default App;