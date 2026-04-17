let routeLine = null;
let visitedMarkersLayer = null;

async function showRoute() {
  const response = await fetch('../show_route_js/visited_route.json');
  const airports = await response.json();

  const routeCoords = airports.map(airport => [airport.lat, airport.lng]);

  if (routeLine) {
    map.removeLayer(routeLine);
  }
  if (visitedMarkersLayer) {
    map.removeLayer(visitedMarkersLayer);
  }

  if (routeCoords.length > 1) {
    routeLine = L.polyline(routeCoords, {
      color: 'red',
      weight: 4,
      opacity: 0.8
    }).addTo(map);

    const markers = airports.map(airport => {
    return L.marker([airport.lat, airport.lng])
      .bindPopup(airport.name);
  });

  visitedMarkersLayer = L.layerGroup(markers).addTo(map);

    map.fitBounds(routeLine.getBounds(), {
      padding: [100, 100]
    });
  }
}
const button = document.querySelector('#show_route')
button.addEventListener('click', async function () {
  await showRoute();
});