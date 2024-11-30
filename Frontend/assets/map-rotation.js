
//import * as L from 'leaflet';

console.log('Script loaded');  // Check if the script itself loads
window.addEventListener('load', function () {
    console.log('The page has fully loaded including all resources.');
    // Use the correct ID for the Leaflet map
    //const mapElement = document.getElementById('map');
    const rootElement = document.body;  // Or some lower-level div if you know it

    // Traverse down through child elements to find the nested map
    let mapElement;
    function findLeafletMap(element) {
        // Iterate through children of current element
        for (let i = 0; i < element.children.length; i++) {
            const child = element.children[i];
            if (child.ID === '#map') {  // Adjust based on actual classes
                mapElement = child;
                return true;  // Stop search once found
            } else {
                if (findLeafletMap(child)) {
                    return true;  // Propagate success upwards
                }
            }
        }
        return false;  // Not found in this branch
    }

    if (findLeafletMap(rootElement)) {
        console.log('Leaflet map found:', mapElement);
        // Use mapElement for further operations
    } else {
        console.error('Leaflet map container not found.');
    }

    const divElement = document.getElementById('react-entry-point');
    if (divElement) {
        console.log('Div element found:', divElement);
        const bgElement = divElement.querySelector('.bg-light.container-fluids');
        if (bgElement) {
            console.log('bgElement found:', bgElement);
            const rowElement = bgElement.querySelector('.g-1.row');
            if (rowElement) {
                console.log('rowElement found:', rowElement);
                const colElement = rowElement.querySelector('.col');
                if (colElement) {
                    console.log('colElement found:', colElement);
                } else{
                    console.error('colElement not found.');
                }
            } else{
                console.error('row Element not found.');
            }
        }
        else {
            console.error('BgElement not found.');
        }
        if (mapElement) {
            console.log('Map element found:', mapElement);
            const leafletMap = mapElement.querySelector('.leaflet-container');  // Adjust selector based on observation
            if (leafletMap) {
                console.log('Leaflet map found:', leafletMap);
                // Perform additional operations on the Leaflet map here
            } else {
                console.error('Leaflet map container not found within the map element.');
            }
        }
        else {
            console.error('mapElement not found');
        }
    }
    if (mapElement) {
        const map = L.map(mapElement, {
            center: [53.5511, 9.9937], // Adjust to your initial coordinates if necessary
            zoom: 14,
            rotation: true  // Enable rotation
        });

        // Adding tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
        }).addTo(map);

        // Function to rotate the map by a specified angle
        function rotateMap(angle) {
            map.setRotation(angle);
        }

        // Adding rotation buttons for interaction
        const rotationControlDiv = L.control({ position: 'bottomleft' });

        rotationControlDiv.onAdd = function () {
            const div = L.DomUtil.create('div', 'rotation-control');
            const rotateLeftButton = L.DomUtil.create('button', '', div);
            rotateLeftButton.innerHTML = 'Rotate Left';
            rotateLeftButton.style.margin = '5px'; // Add some margin for spacing
            rotateLeftButton.onclick = function() {
                const currentRotation = map.getRotation();
                rotateMap(currentRotation - 15);  // Rotate left by 15 degrees
            };

            const rotateRightButton = L.DomUtil.create('button', '', div);
            rotateRightButton.innerHTML = 'Rotate Right';
            rotateRightButton.style.margin = '5px';
            rotateRightButton.onclick = function() {
                const currentRotation = map.getRotation();
                rotateMap(currentRotation + 15);  // Rotate right by 15 degrees
            };

            // Style for the control
            div.style.display = "flex";  // Arrange buttons in a column
            div.style.flexDirection = "column";
            div.style.padding = "10px";
            div.style.backgroundColor = "white";
            div.style.border = "1px solid black"; // Add a border to improve visibility
            div.style.borderRadius = "5px"; // Rounded edges
            div.style.boxShadow = "2px 2px 5px rgba(0, 0, 0, 0.5)"; // Shadow for depth

            return div;
        };

        // Add the control to the map
        rotationControlDiv.addTo(map);
    } else {
        console.error("Map element not found!");
    }
});


/*window.addEventListener('load', function () {
    const map = L.map('map', {
        center: [53.5511, 9.9937],
        zoom: 14,
        rotation: true  // Enable rotation
    });

    // Adding tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
    }).addTo(map);

    
    // Optional: Add rotation control
    L.control.rotate({position: 'topright'}).addTo(map);

    // Rotation event listener
    map.on('rotateend', function (event) {
        console.log("Map rotated to: " + event.target.getBearing());
    });
});
*/
//var map = L.map('map', {rotate: true})
