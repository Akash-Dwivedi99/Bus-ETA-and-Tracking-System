// ===============================
// 1. Create the map
// ===============================

const map = L.map("map").setView([30.3426, 77.9250], 13);


// ===============================
// 2. Add OpenStreetMap
// ===============================

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors"
}).addTo(map);


// ===============================
// 3. Bus marker variable
// ===============================

let busMarker = null;


// ===============================
// 4. Flask API URL
// ===============================

const API_URL =
    "http://127.0.0.1:5000/api/bus-location?bus_id=bus-1";


// ===============================
// 5. Get bus data from Flask
// ===============================

async function fetchBusData() {

    try {

        const response = await fetch(API_URL);

        const data = await response.json();

        console.log("Bus data:", data);


        // ===============================
        // 6. Get bus latitude & longitude
        // ===============================

        const busLat = data.lat;
        const busLng = data.lng;


        // ===============================
        // 7. Create bus marker
        // ===============================

        if (busMarker === null) {

            busMarker = L.marker([busLat, busLng])
                .addTo(map)
                .bindPopup("🚌 Bus 01");

        } 
        
        // ===============================
        // 8. Move existing marker
        // ===============================

        else {

            busMarker.setLatLng([busLat, busLng]);

        }


        // ===============================
        // 9. Update ETA
        // ===============================

        document.getElementById("eta").innerText =
            data.eta_minutes + " minutes";


    } catch (error) {

        console.error("Error fetching bus data:", error);

    }
}


// ===============================
// 10. First API call
// ===============================

fetchBusData();


// ===============================
// 11. Repeat every 5 seconds
// ===============================

setInterval(fetchBusData, 5000);