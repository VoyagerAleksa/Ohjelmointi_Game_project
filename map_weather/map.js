const default_position = [60.31896301700641, 24.9678752369183];

const key = 'FrMSh0rZXij8VQlwBM3v';
const map = L.map('map').setView(default_position, 6);

L.maptiler.maptilerLayer({
  apiKey: key,
  style: "https://api.maptiler.com/maps/019dd959-84c1-7825-acea-dda99483f25e/style.json?key=FrMSh0rZXij8VQlwBM3v",
}).addTo(map);

const planeIcon = L.icon({
  iconUrl: '../assets/vodka.gif',
  iconSize: [55, 55],
  iconAnchor: [18, 18],
  popupAnchor: [0, -18]
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
let currentHeading = 0;
let animationFrame = null;
let isUpdating = false;

function shortestAngleDelta(from, to) {
  return ((to - from + 540) % 360) - 180;
}

function animatePlane(marker, fromCoords, toCoords, newHeading, duration = 1500) {
  if (animationFrame) {
    cancelAnimationFrame(animationFrame);
  }

  const start = performance.now();
  const fromLat = fromCoords[0];
  const fromLng = fromCoords[1];
  const toLat = toCoords[0];
  const toLng = toCoords[1];

  const startHeading = currentHeading;
  const headingDelta = shortestAngleDelta(startHeading, newHeading);

  function step(now) {
    const t = Math.min((now - start) / duration, 1);

    const lat = fromLat + (toLat - fromLat) * t;
    const lng = fromLng + (toLng - fromLng) * t;
    const heading = startHeading + headingDelta * t;

    marker.setLatLng([lat, lng]);
    marker.setRotationAngle(heading);

    if (t < 1) {
      animationFrame = requestAnimationFrame(step);
    } else {
      currentHeading = newHeading;
      animationFrame = null;
    }
  }

  animationFrame = requestAnimationFrame(step);
}

async function updateLocation() {
  if (isUpdating) return;
  isUpdating = true;

  try {
    const response = await fetch('current_location.json?' + Date.now());
    const current_location = await response.json();
    const current_coords = [current_location.lat, current_location.lng];
    const direction = current_location.heading ?? 0;
    const distance = current_location.distance ?? 0;

    const locationChanged =
      !lastLocation ||
      lastLocation[0] !== current_location.lat ||
      lastLocation[1] !== current_location.lng;

    rotateCompassSmooth(direction);
    updateCompassDistance(distance);

    const weather = await getWeather(current_location.lat, current_location.lng);
    const weatherInfo = getWeatherInfo(weather.weather_code);

    const popupHtml = `
      <div class="weather-popup">
        <div class="weather-popup__title">
          ${current_location.name || 'Current location'}
        </div>

        <div class="weather-popup__status">
          <span class="weather-popup__icon">${weatherInfo.icon}</span>
          <span class="weather-popup__text">${weatherInfo.text}</span>
        </div>

        <div class="weather-popup__row">
          <span class="weather-popup__label">Temperature</span>
          <span class="weather-popup__value">${weather.temperature_2m} °C</span>
        </div>

        <div class="weather-popup__row">
          <span class="weather-popup__label">Wind</span>
          <span class="weather-popup__value">${weather.wind_speed_10m} km/h</span>
        </div>
      </div>
    `;

    const popupOptions = {
      className: 'game-popup',
      maxWidth: 240,
      minWidth: 210,
      offset: [0, -8]
    };

    if (!marker) {
      marker = L.marker(current_coords, {
        icon: planeIcon,
        rotationAngle: direction,
        rotationOrigin: 'center center'
      }).addTo(map).bindPopup(popupHtml, popupOptions);

      currentHeading = direction;
    } else {
      marker.setPopupContent(popupHtml);

      if (locationChanged) {
        animatePlane(marker, lastLocation, current_coords, direction, 1800);
      } else {
        marker.setRotationAngle(direction);
        currentHeading = direction;
      }
    }

    if (locationChanged) {
      map.flyTo(current_coords, 5, {
        animate: true,
        duration: 3
      });
      lastLocation = current_coords;
    }
  } catch (error) {
    console.error('updateLocation error:', error);
  } finally {
    isUpdating = false;
  }
}

updateLocation();
setInterval(updateLocation, 2000);

//Victory screen invocation
//showVictory({
//  airports: ['HEL', 'ARN', 'CPH', 'AMS', 'FRA'],
//  time: '12:34',
//  points: 870
//});