async function getWeather(lat, lng) {
  const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lng}&current=temperature_2m,wind_speed_10m,weather_code`;
  const response = await fetch(url);
  const weatherData = await response.json();
  return weatherData.current;
}

function getWeatherInfo(code) {
  const weatherMap = {
    0:  { icon: "☀️", text: "Clear sky" },
    1:  { icon: "🌤️", text: "Mainly clear" },
    2:  { icon: "⛅", text: "Partly cloudy" },
    3:  { icon: "☁️", text: "Overcast" },
    45: { icon: "🌫️", text: "Fog" },
    48: { icon: "🌫️", text: "Rime fog" },
    51: { icon: "🌦️", text: "Light drizzle" },
    53: { icon: "🌦️", text: "Moderate drizzle" },
    55: { icon: "🌧️", text: "Dense drizzle" },
    56: { icon: "🌧️", text: "Freezing drizzle" },
    57: { icon: "🌧️", text: "Dense freezing drizzle" },
    61: { icon: "🌧️", text: "Light rain" },
    63: { icon: "🌧️", text: "Rain" },
    65: { icon: "🌧️", text: "Heavy rain" },
    66: { icon: "🌧️", text: "Freezing rain" },
    67: { icon: "🌧️", text: "Heavy freezing rain" },
    71: { icon: "🌨️", text: "Light snow" },
    73: { icon: "🌨️", text: "Snow" },
    75: { icon: "❄️", text: "Heavy snow" },
    77: { icon: "🌨️", text: "Snow grains" },
    80: { icon: "🌦️", text: "Rain showers" },
    81: { icon: "🌧️", text: "Heavy rain showers" },
    82: { icon: "⛈️", text: "Violent rain showers" },
    85: { icon: "🌨️", text: "Snow showers" },
    86: { icon: "❄️", text: "Heavy snow showers" },
    95: { icon: "⛈️", text: "Thunderstorm" },
    96: { icon: "⛈️", text: "Thunderstorm with hail" },
    99: { icon: "⛈️", text: "Heavy hail thunderstorm" }
  };
  return weatherMap[code] || { icon: "❓", text: "Unknown weather" };
}