const default_position = [60.31896301700641, 24.9678752369183];

const key = 'FrMSh0rZXij8VQlwBM3v';
const map = L.map('map').setView(default_position, 6);

L.maptiler.maptilerLayer({
  apiKey: key,
  style: "https://api.maptiler.com/maps/019dd959-84c1-7825-acea-dda99483f25e/style.json?key=FrMSh0rZXij8VQlwBM3v",
}).addTo(map);

const aircraftDisplayNames = {
  small: 'ATR 72',
  medium: 'Boeing 737',
  large: 'Airbus A380'
};

const planeIcons = {
  small: L.icon({
    iconUrl: '../assets/plane_small.png',
    iconSize: [42, 42],
    iconAnchor: [21, 21],
    popupAnchor: [0, -18]
  }),
  medium: L.icon({
    iconUrl: '../assets/plane_medium.png',
    iconSize: [55, 55],
    iconAnchor: [27, 27],
    popupAnchor: [0, -18]
  }),
  large: L.icon({
    iconUrl: '../assets/plane_large.png',
    iconSize: [72, 72],
    iconAnchor: [36, 36],
    popupAnchor: [0, -18]
  })
};

function getPlaneIcon(type) {
  return planeIcons[type] || planeIcons.medium;
}

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

function updateDataPanel(currentLocation) {
  const aircraftType = currentLocation.aircraft_type || 'medium';

  const aircraftTypeEl = document.getElementById('aircraft-type');
  const aircraftNameEl = document.getElementById('aircraft-name');
  const flightCo2El = document.getElementById('flight-co2');
  const sessionCo2El = document.getElementById('session-co2');
  const flightDistanceEl = document.getElementById('flight-distance');

  if (aircraftTypeEl) aircraftTypeEl.textContent = aircraftType.toUpperCase();
  if (aircraftNameEl) aircraftNameEl.textContent = currentLocation.aircraft_name || aircraftDisplayNames[aircraftType] || 'Unknown aircraft';
  if (flightCo2El) flightCo2El.textContent = `${Number(currentLocation.flight_co2 || 0).toFixed(2)} kg`;
  if (sessionCo2El) sessionCo2El.textContent = `${Number(currentLocation.session_co2 || 0).toFixed(2)} kg`;
  if (flightDistanceEl) flightDistanceEl.textContent = `${Math.round(currentLocation.flight_distance || 0)} km`;
}

let marker = null;
let lastLocation = null;
let currentHeading = 0;
let animationFrame = null;
let isUpdating = false;

function animatePlaneArc(marker, fromCoords, toCoords, duration = 2200, arcHeight = 0.18) {
  if (animationFrame) {
    cancelAnimationFrame(animationFrame);
  }

  const start = performance.now();

  const p0 = { lat: fromCoords[0], lng: fromCoords[1] };
  const p2 = { lat: toCoords[0], lng: toCoords[1] };

  const mid = {
    lat: (p0.lat + p2.lat) / 2,
    lng: (p0.lng + p2.lng) / 2
  };

  const dx = p2.lng - p0.lng;
  const dy = p2.lat - p0.lat;
  const dist = Math.sqrt(dx * dx + dy * dy) || 0.0001;

  const nx = -dy / dist;
  const ny = dx / dist;
  const curveAmount = dist * arcHeight;

  const p1 = {
    lat: mid.lat + ny * curveAmount,
    lng: mid.lng + nx * curveAmount
  };

  function bezierPoint(t) {
    const oneMinusT = 1 - t;
    return {
      lat: oneMinusT * oneMinusT * p0.lat +
           2 * oneMinusT * t * p1.lat +
           t * t * p2.lat,
      lng: oneMinusT * oneMinusT * p0.lng +
           2 * oneMinusT * t * p1.lng +
           t * t * p2.lng
    };
  }

  function bezierTangent(t) {
    return {
      lat: 2 * (1 - t) * (p1.lat - p0.lat) + 2 * t * (p2.lat - p1.lat),
      lng: 2 * (1 - t) * (p1.lng - p0.lng) + 2 * t * (p2.lng - p1.lng)
    };
  }

  function step(now) {
    const tRaw = Math.min((now - start) / duration, 1);
    const t = tRaw < 0.5
      ? 2 * tRaw * tRaw
      : 1 - Math.pow(-2 * tRaw + 2, 2) / 2;

    const pos = bezierPoint(t);
    const tan = bezierTangent(t);
    const angle = Math.atan2(tan.lng, tan.lat) * 180 / Math.PI;

    marker.setLatLng([pos.lat, pos.lng]);
    marker.setRotationAngle(angle);

    if (tRaw < 1) {
      animationFrame = requestAnimationFrame(step);
    } else {
      currentHeading = angle;
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
    const currentLocation = await response.json();
    const currentCoords = [currentLocation.lat, currentLocation.lng];
    const direction = currentLocation.heading ?? 0;
    const mDirection = currentLocation.m_direction ?? 0;
    const aircraftType = currentLocation.aircraft_type || 'medium';
    const distanceToLuggage = currentLocation.distance_to_luggage ?? 0;

    const locationChanged =
      !lastLocation ||
      lastLocation[0] !== currentLocation.lat ||
      lastLocation[1] !== currentLocation.lng;

    rotateCompassSmooth(direction);
    updateCompassDistance(distanceToLuggage);
    updateDataPanel(currentLocation);

    const weather = await getWeather(currentLocation.lat, currentLocation.lng);
    const weatherInfo = getWeatherInfo(weather.weather_code);

    const popupHtml = `
      <div class="weather-popup">
        <div class="weather-popup__title">
          ${currentLocation.name || 'Current location'}
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
      marker = L.marker(currentCoords, {
        icon: getPlaneIcon(aircraftType),
        rotationAngle: mDirection,
        rotationOrigin: 'center center'
      }).addTo(map).bindPopup(popupHtml, popupOptions);

      currentHeading = mDirection;
    } else {
      marker.setPopupContent(popupHtml);
      marker.setIcon(getPlaneIcon(aircraftType));

      if (locationChanged && lastLocation) {
        animatePlaneArc(marker, lastLocation, currentCoords, 2200, 0.18);
      } else {
        marker.setLatLng(currentCoords);
      }
    }

    if (locationChanged) {
      map.flyTo(currentCoords, 5, {
        animate: true,
        duration: 3
      });
      lastLocation = currentCoords;
    }
  } catch (error) {
    console.error('updateLocation error:', error);
  } finally {
    isUpdating = false;
  }
}

updateLocation();
setInterval(updateLocation, 2000);