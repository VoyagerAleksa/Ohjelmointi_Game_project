const default_position = [60.31896301700641, 24.9678752369183]
const map = L.map('map').setView(default_position, 6);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

const redIcon = L.icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

async function getWeather(lat, lng) {
  const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lng}&current=temperature_2m,wind_speed_10m,weather_code`;

  const response = await fetch(url);
  const weather_data = await response.json();
  return weather_data.current;
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

  return weatherMap[code]
}


let marker = null;
let lastLocation = null;
async function updateLocation() {
  const response = await fetch('current_location.json?' + Date.now());
  const current_location = await response.json();
  const current_coords = [current_location.lat, current_location.lng]

   const locationChanged =
      !lastLocation ||
      lastLocation[0] !== current_location.lat ||
      lastLocation[1] !== current_location.lng;

  const weather = await getWeather(current_location.lat, current_location.lng);
  const weatherInfo = getWeatherInfo(weather.weather_code);

  const popupHtml = `
    <div style="min-width: 190px; line-height: 1.45;">
      <div style="font-weight: 700; font-size: 15px; margin-bottom: 8px;">
        ${current_location.name || 'Current location'}
      </div>
      <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
        <span style="font-size: 24px;">${weatherInfo.icon}</span>
        <span>${weatherInfo.text}</span>
      </div>
      <div><strong>Temperature:</strong> ${weather.temperature_2m} °C</div>
      <div><strong>Wind:</strong> ${weather.wind_speed_10m} km/h</div>
    </div>
  `;

  if (!marker) {
        marker = L.marker([current_location.lat, current_location.lng], { icon: redIcon })
            .addTo(map)
            .bindPopup(popupHtml)
        }
  else {
        marker.setLatLng([current_location.lat, current_location.lng]);
        marker.setPopupContent(popupHtml);
    }
  if (locationChanged) {
    map.flyTo(current_coords, 5, {
      animate: true,
      duration: 3
    });
    lastLocation = current_coords
  }
}

updateLocation()
setInterval(updateLocation, 2000);