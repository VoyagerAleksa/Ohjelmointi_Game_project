const default_position = [60.31896301700641, 24.9678752369183];

const key = 'FrMSh0rZXij8VQlwBM3v';
      const map = L.map('map').setView(default_position, 6);
      const mtLayer = L.maptiler.maptilerLayer({
        apiKey: key,
        style: "https://api.maptiler.com/maps/019dd959-84c1-7825-acea-dda99483f25e/style.json?key=FrMSh0rZXij8VQlwBM3v", //optional
      }).addTo(map);

/*L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);*/

const redIcon = L.icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

let compassBase = null;
let currentRotation = 0;

const Compass = L.Control.extend({
  options: {
    position: 'topright'
  },

  onAdd: function () {
    const div = L.DomUtil.create('div', 'compass-control');

    div.innerHTML = `
      <div class="compass-wrap">
        <img src="../assets/Compass.png" alt="compass" class="compass-base">
        <div class="compass-arrow"></div>
        <div class="compass-distance" id="compass-distance">0 km</div>
      </div>
    `;

    compassBase = div.querySelector('.compass-base');
    return div;
  }
});

map.addControl(new Compass());

function rotateCompassSmooth(targetAngle) {
  if (!compassBase) return;

  let delta = ((targetAngle - currentRotation + 540) % 360) - 180;
  currentRotation += delta;

  compassBase.style.transform = `rotate(${currentRotation}deg)`;
}

function updateCompassDistance(distanceKm) {
  const distanceEl = document.getElementById('compass-distance');
  if (distanceEl) {
    distanceEl.textContent = `${Math.round(distanceKm)} km`;
  }
}

let marker = null;
let lastLocation = null;

async function updateLocation() {
  const response = await fetch('current_location.json?' + Date.now());
  const current_location = await response.json();
  const current_coords = [current_location.lat, current_location.lng];
  const direction = current_location.heading
  const distance = current_location.distance

  const locationChanged =
    !lastLocation ||
    lastLocation[0] !== current_location.lat ||
    lastLocation[1] !== current_location.lng;

  rotateCompassSmooth(direction)
  updateCompassDistance(distance)

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
      .bindPopup(popupHtml);
  } else {
    marker.setLatLng([current_location.lat, current_location.lng]);
    marker.setPopupContent(popupHtml);
  }

  if (locationChanged) {
    map.flyTo(current_coords, 5, {
      animate: true,
      duration: 3
    });
    lastLocation = current_coords;
  }
}

updateLocation();
setInterval(updateLocation, 2000);

//Victory screen invocation
showVictory({
  airports: ['HEL', 'ARN', 'CPH', 'AMS', 'FRA'],  // Keep the component static for now
  time: '12:34',                                     // Keep the component static for now
  points: 870                                        // Keep the component static for now
});
