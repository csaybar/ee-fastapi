var origin = "http://0.0.0.0"
var port = "80"
    
// raster layer (OSM)
var raster = new ol.layer.Tile({    
    title:"OSM basemap",
    source: new ol.source.OSM(),
})

// vector layer (bbox)
var source = new ol.source.Vector({wrapX: false});
var vector = new ol.layer.Vector({
    title:"geometry",
    source: source,    
});

// Map Creator
function CreateMap(layers) {
    var map = new ol.Map({
        target: 'map',
        layers: layers,
        view: new ol.View({
            center: ol.proj.transform([34.09, -17.87], 'EPSG:4326', 'EPSG:3857'),
            zoom: 8
        })    
    });
    return map        
}

var map = CreateMap(layers=[raster, vector]);

// Add sidebar
var sidebar = new ol.control.Sidebar({ element: 'sidebar', position: 'left' });
map.addControl(sidebar);

// Draw a box
var draw; // global so we can remove it later
function addInteraction() {        
    draw = new ol.interaction.Draw({
        source: source,
        type: "Circle",
        geometryFunction: ol.interaction.Draw.createBox()
    });

    // Add vector draw layer to the main map
    map.addInteraction(draw);
}

// Handle change event.
document.getElementById('undo').addEventListener('click', function () {
    map.getLayers().getArray().forEach(layer => {
      if (layer.values_.title == "Flood Area" | layer.values_.title == "After Flood" | layer.values_.title == "Before Flood"){
          map.removeLayer(layer)
      }
    });
    
    map.getLayers().getArray().forEach(layer => {
      if (layer.values_.title == "Flood Area" | layer.values_.title == "After Flood" | layer.values_.title == "Before Flood"){
          map.removeLayer(layer)
      }
    });
    
    var features = source.getFeatures();
    var lastFeature = features[features.length - 1];    
    source.removeFeature(lastFeature);
});
  
// Handle change event.
document.getElementById('download').addEventListener('click', function () {
    
    document.getElementById('download').value = '...'

    // Obtain ROI
    var features = source.getFeatures();
    var lastFeature = features[features.length - 1].clone();
    var bbox = lastFeature.getGeometry().transform('EPSG:3857', 'EPSG:4326').getExtent().toString();
    
    // Obtain Dates
    var init_start = document.getElementById("init_start").value;
    var init_last = document.getElementById("init_last").value;
    
    var flood_start = document.getElementById("flood_start").value;
    var flood_last = document.getElementById("flood_last").value;

    // Obtain threshold
    var flood_threshold = document.getElementById("threshold").value;
    
    const request = new Request(
        origin.concat(":").concat(port).concat("/flood_download/"), 
        {
            method: 'POST',
            body: JSON.stringify(
                {
                    bbox: bbox,
                    init_start: init_start,
                    init_last: init_last,
                    flood_start: flood_start,
                    flood_last: flood_last,
                    flood_threshold: flood_threshold
                }
            )
        }
    );

    fetch(request)
    .then(response => {
        if (response.status === 200) {
          return response.json();
        } else {
          throw new Error('Something went wrong on api server!');
        }
      })
      .then(response => {
        document.location.href = origin.concat(":").concat(port).concat("/").concat(response);
        document.getElementById('download').value = 'download'
      }).catch(error => {
        console.error(error);
      });      
});

// Handle change event.
document.getElementById('display').addEventListener('click', function () {
    
    document.getElementById('display').value = '...'
    
    // Obtain ROI
    var features = source.getFeatures();
    var lastFeature = features[features.length - 1].clone();
    var bbox = lastFeature.getGeometry().transform('EPSG:3857', 'EPSG:4326').getExtent().toString();
    
    // Obtain Dates
    var init_start = document.getElementById("init_start").value;
    var init_last = document.getElementById("init_last").value;
    
    var flood_start = document.getElementById("flood_start").value;
    var flood_last = document.getElementById("flood_last").value;

    // Obtain threshold
    var flood_threshold = document.getElementById("threshold").value;
    
    const request = new Request(
        origin.concat(":").concat(port).concat("/flood_display/"), 
        {
            method: 'POST',
            body: JSON.stringify(
                {
                    bbox: bbox,
                    init_start: init_start,
                    init_last: init_last,
                    flood_start: flood_start,
                    flood_last: flood_last,
                    flood_threshold: flood_threshold
                }
            )
        }
    );

    fetch(request)
    .then(response => {
        if (response.status === 200) {
          return response.json();
        } else {
          throw new Error('Something went wrong on api server!');
        }
      })
      .then(response => {
        // Before Flood
        bflood = new ol.layer.Tile({
          source: new ol.source.XYZ({            
            url: response["before_flood"]            
          }),
          title: "Before Flood"
        });
        // After Flood
        aflood = new ol.layer.Tile({
          source: new ol.source.XYZ({            
            url: response["after_flood"]            
          }),
          title: "After Flood",
        });

        // Flood Area
        final = new ol.layer.Tile({
          source: new ol.source.XYZ({            
            url: response["s1_fresults_id"]            
          }),
          title: "Flood Area"
        });
        
        map.addLayer(final);
        map.addLayer(aflood);
        map.addLayer(bflood);
        
        var layerSwitcher = new ol.control.LayerSwitcher();
        map.addControl(layerSwitcher);
        document.getElementById('display').value = 'display'

      }).catch(error => {
        console.error(error);
      });
});

addInteraction()