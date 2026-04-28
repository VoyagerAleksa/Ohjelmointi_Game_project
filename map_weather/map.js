const default_position = [60.31896301700641, 24.9678752369183];
const map = L.map('map').setView(default_position, 6);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

let compassImg = null;
let compassVersion = 0;

const Compass = L.Control.extend({
  options: {
    position: 'topright'
  },

  onAdd: function () {
    const div = L.DomUtil.create('div', 'compass-control');

    compassImg = L.DomUtil.create('img', '', div);
    compassImg.alt = 'compass';
    compassImg.style.width = '300px';
    compassImg.style.height = '300px';
    compassImg.src = `../compass.png?v=${Date.now()}`;

    return div;
  }
});

map.addControl(new Compass());

function updateCompassImage() {
  if (!compassImg) return;

  const nextSrc = `../compass.png?v=${Date.now()}_${compassVersion++}`;
  const preloader = new Image();

  preloader.onload = function () {
    compassImg.src = nextSrc;
    console.log('compass updated:', nextSrc);
  };

  preloader.onerror = function () {
    console.log('new compass image not ready yet');
  };

  preloader.src = nextSrc;
}

const redIcon = L.icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

let marker = null;
let lastLocation = null;

async function updateLocation() {
  const response = await fetch('current_location.json?' + Date.now());
  const current_location = await response.json();
  const current_coords = [current_location.lat, current_location.lng];

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
updateCompassImage()
setInterval(updateCompassImage, 1500);