var map;
var infoWindow;

function initialize() {
  var myLatLng = new google.maps.LatLng(24.886436490787712, -70.2685546875);
  var mapOptions = {
    zoom: 5,
    center: myLatLng,
    mapTypeId: google.maps.MapTypeId.TERRAIN
  };

  var district;

  map = new google.maps.Map(document.getElementById('map_canvas'),
      mapOptions);

  var districtCoords = [
      new google.maps.LatLng(25.774252, -80.190262),
      new google.maps.LatLng(18.466465, -66.118292),
      new google.maps.LatLng(32.321384, -64.75737)
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

  var contentString = '<b>district</b><br>';
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
