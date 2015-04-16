Map {
  background-color: darken(#b8dee6,70);
}

#countries,
#landpolygons {
  line-color: #899;
  line-width: 1;
  line-join: round;
  polygon-fill: black;
  polygon-opacity: 1;
}

#rasterextents {
  line-color:#594;
  line-width:2;
  polygon-opacity:0.1;
  polygon-fill:#ae8;
}

#latlonextents {
  line-color:salmon;
  line-width:0.5;
  polygon-opacity:0.1;
  polygon-fill:salmon;
}

@linewidth: 0;

@stop0: 0;
@stop1: 0.0001;
@stop2: 10;
@stop3: 100;
@stop4: 500;
@stop5: 1000;
@stop6: 3000;
@stop7: 10000;
@stop8: 50000;
@stop9: 100000;

#glcount00 {
  comp-op: lighten;
  raster-opacity: 1;
  raster-scaling: near;
  raster-colorizer-default-mode:linear;
  raster-colorizer-default-color: transparent;
  raster-colorizer-epsilon:0.41;
  // For some reason there are negative values? this will help us spot them.
  // dark gray for zero population... ocean mainly. But also northern canada and greenland
  // black for very low population, siberia, australia, etc

  raster-colorizer-stops:
    stop(@stop0,transparent)
    stop(@stop4,darken(#cd570c,20))
    stop(@stop7,#cd570c)
    stop(@stop9,white)
}

.raster {
  raster-opacity:1;
  comp-op: overlay;
  raster-scaling: near;
  raster-colorizer-default-mode:linear;
  raster-colorizer-default-color: transparent;
  raster-colorizer-epsilon:0.41;
  raster-colorizer-stops:
    stop(0,transparent)
    stop(10,red)
    stop(500,blue)
    stop(1000,white)
}
