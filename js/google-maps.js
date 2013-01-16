var map;
var infoWindow;

function initialize() {
  var cLatLon = new google.visualization.Query()
  var myLatLng = new google.maps.LatLng(44.9303955, -93.047638);
  var mapOptions = {
    zoom: 5,
    center: myLatLng,
    mapTypeId: google.maps.MapTypeId.TERRAIN
  };

  var district;

  map = new google.maps.Map(document.getElementById('map_canvas'),
      mapOptions);

  var districtCoords = [
      new google.maps.LatLng(44.964332, -93.090956),
      new google.maps.LatLng(44.966795, -93.090551),
      new google.maps.LatLng(44.970041, -93.088913),
      new google.maps.LatLng(44.969877, -93.087756),
      new google.maps.LatLng(44.9691, -93.088663),
      new google.maps.LatLng(44.968265, -93.087978),
      new google.maps.LatLng(44.968087, -93.085514),
      new google.maps.LatLng(44.966509, -93.085531),
      new google.maps.LatLng(44.966592, -93.076087),
      new google.maps.LatLng(44.962981, -93.076089),
      new google.maps.LatLng(44.963083, -93.025319),
      new google.maps.LatLng(44.967721, -93.025296),
      new google.maps.LatLng(44.967729, -93.020237),
      new google.maps.LatLng(44.969088, -93.015176),
      new google.maps.LatLng(44.969203, -93.008335),
      new google.maps.LatLng(44.969054, -93.006538),
      new google.maps.LatLng(44.968559, -93.005113),
      new google.maps.LatLng(44.919443, -93.004816),
      new google.maps.LatLng(44.890767, -93.00432),
      new google.maps.LatLng(44.89075, -93.020044),
      new google.maps.LatLng(44.894074, -93.024607),
      new google.maps.LatLng(44.897831, -93.034733),
      new google.maps.LatLng(44.905101, -93.042125),
      new google.maps.LatLng(44.912307, -93.045179),
      new google.maps.LatLng(44.9195, -93.050252),
      new google.maps.LatLng(44.919501, -93.050888),
      new google.maps.LatLng(44.919924, -93.04985),
      new google.maps.LatLng(44.920312, -93.050297),
      new google.maps.LatLng(44.923026, -93.051228),
      new google.maps.LatLng(44.926003, -93.050745),
      new google.maps.LatLng(44.927788, -93.049682),
      new google.maps.LatLng(44.931822, -93.049451),
      new google.maps.LatLng(44.934744, -93.049937),
      new google.maps.LatLng(44.938584, -93.052123),
      new google.maps.LatLng(44.942196, -93.056676),
      new google.maps.LatLng(44.944865, -93.063217),
      new google.maps.LatLng(44.946008, -93.061804),
      new google.maps.LatLng(44.95073, -93.075313),
      new google.maps.LatLng(44.951962, -93.076612),
      new google.maps.LatLng(44.954478, -93.077948),
      new google.maps.LatLng(44.954605, -93.078747),
      new google.maps.LatLng(44.955624, -93.078886),
      new google.maps.LatLng(44.955435, -93.079317),
      new google.maps.LatLng(44.957983, -93.082238),
      new google.maps.LatLng(44.957865, -93.09073),
      new google.maps.LatLng(44.963476, -93.090703),
      new google.maps.LatLng(44.963505, -93.090942),
      new google.maps.LatLng(44.964332, -93.090956)
  ];

  district = new google.maps.Polygon({
    paths: districtCoords,
    strokeColor: '#FF0000',
    strokeOpacity: 0.8,
    strokeWeight: 3,
    fillColor: '#FF0000',
    fillOpacity: 0.35
  });

  district.setMap(map);

  // Add a listener for the click event
  google.maps.event.addListener(district, 'click', showArrays);

  infowindow = new google.maps.InfoWindow();
}

function showArrays(event) {

  // Since this Polygon only has one path, we can call getPath()
  // to return the MVCArray of LatLngs
  var vertices = this.getPath();

  var contentString = '<b>Legislative district</b><br>';
  contentString += 'Clicked Location: <br>' + event.latLng.lat() + ',' + event.latLng.lng() + '<br>';

  // Iterate over the vertices.
  for (var i =0; i < vertices.length; i++) {
    var xy = vertices.getAt(i);
    contentString += '<br>' + 'Coordinate: ' + i + '<br>' + xy.lat() +',' + xy.lng();
  }

  // Replace our Info Window's content and position
  infowindow.setContent(contentString);
  infowindow.setPosition(event.latLng);

  infowindow.open(map);
}