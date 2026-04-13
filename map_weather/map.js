const current_position = [60.31896301700641, 24.9678752369183]
const map = L.map('map').setView(current_position, 6);
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

let marker = null;
let lastLocation = null;
async function updateLocation() {
  const response = await fetch('current_location.json?' + Date.now());
  const data = await response.json();
  const coords = [data.lat, data.lng]

   const locationChanged =
      !lastLocation ||
      lastLocation[0] !== data.lat ||
      lastLocation[1] !== data.lng;

  if (!marker) {
        marker = L.marker([data.lat, data.lng], { icon: redIcon })
            .addTo(map)
            .bindPopup("You are here")
            .openPopup();
        }
  else {
        marker.setLatLng([data.lat, data.lng]);
    }
  if (locationChanged) {
    map.flyTo(coords, 5, {
      animate: true,
      duration: 3
    });
    lastLocation = coords
  }
}

updateLocation()
setInterval(updateLocation, 2000);