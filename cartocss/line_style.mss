/*
Map {
  background-color: white;
}

#histline {
  line-color: blue;
  line-opacity: 0.01;
}
*/

#londonblankspots1000 {
  [zoom = 9] { 
    marker-width:2; 
    marker-line-width:0.5;
  }
  [zoom = 10] { 
    marker-width:3; 
    marker-line-width:0.5;
  }
  [zoom = 11] { 
    marker-width:4; 
  }
  [zoom = 12] { 
    marker-width:5; 
  }
  [zoom = 13] { 
    marker-width:6; 
  }
  [zoom = 14] { 
    marker-width:7; 
  }
  
  marker-fill:yellow;
  marker-line-color:black;
  marker-allow-overlap:true;
  marker-opacity: 0.8;
}
