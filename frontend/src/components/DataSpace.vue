<template>
<div id="AllClass">
  	<div id="BeeSwarm"></div>
    <div id="Sliders"></div>
    <div id="TextLabels"></div>
    <div id="NoAction" style="width: 2525px !important; height: 250px !important;"></div>
</div> 
</template>

<script>

import { EventBus } from '../main.js'
import * as Plotly from 'plotly.js'

export default {
  name: 'DataSpace',
  data () {
    return {
      dataInstances: '',
      PositiveValue: 75,
      NegativeValue: 25,
      storeColor: [],
      status: true,
      rootIDSelected: 1,
    }
  },
  methods: {
    initializeBeeSwarm () {   
      var svg = d3.select("#BeeSwarm");
      svg.selectAll("*").remove();
      
      var tooltip = d3.select("#tooltip")

      var width = 2525
      var height = 250
      var rectWidth = 20
      var rectHeight = 10
      
      var nodeR = 6
      var nodeStrokeW = 1.5
      
      var scale = 1

      var predictions = JSON.parse(this.dataInstances[2])

      var len = predictions.length;
      var instances = new Array(len);
      for (var i = 0; i < len; ++i) instances[i] = i
      instances.sort(function (a, b) { return predictions[a] < predictions[b] ? -1 : predictions[a] > predictions[b] ? 1 : 0; })

      predictions.sort()

      var colorInstances = []

      if (this.status) {
        this.storeColor = []
        for (let i = 0; i < predictions.length; i++) {
          if (predictions[i] > 50 && predictions[i] > this.PositiveValue) {
            colorInstances.push("#33a02c")
          } else if (predictions[i] > 50 && predictions[i] <= this.PositiveValue) {
            colorInstances.push("#b2df8a")
          } else if (predictions[i] <= 50 && predictions[i] > this.NegativeValue) {
            colorInstances.push("#fb9a99")
          } else {
            colorInstances.push("#e31a1c")
          }
        }
        this.storeColor = colorInstances
      } else {
        colorInstances = this.storeColor
      }

      var data = d3.range(instances.length).map(function(d, i) {
        return {
          x : predictions[i],
          y : 0, // doesn't matter, will be reset before it matters
          r : nodeR,
          col: colorInstances[i],
          system : 'Predicted Probability',
          label : '(%)'
        }
      })
      
      var dx = function(d) { return d.x }
      var dy = function(d) { return d.y }
      var dr = function(d) { return d.r }
      var colorX = function(d) { return d.col }
      
      var extent = d3.extent(data, dx)

      // the range is set in such a way that portions of nodes are not drawn outside the g
      var xScale = d3.scale.linear()
        .domain([0,100])
        .range([25, width-25])

      var norm = d3.random.normal(0, 4.0)
      
      var chart = d3.select("#BeeSwarm").append("svg")
          .attr("width", width)
          .attr("height", height)
          .attr("pointer-events", "all")		
        .append("g")
          .attr("transform", "translate(0,0)")
          // .on("mousemove", function() {
          //   var x = d3.event.pageX - 24 // subtract translation
          //   followMe.transition()
          //     .duration(10)
          //     .attr("x1", x).attr("x2", x)
          // })
          // .call(d3.behavior.zoom().x(xScale).scaleExtent([1, 10]).on("zoom", zoom))
        .append('g');
      
      // append a background rectangle to receive the pointer events
      // (otherwise zoom only works when the pointer is over a node)
      chart.append('rect')
        .attr('width', width)
        .attr('height', height)
        .attr('fill', 'white');
      
      var axis = d3.svg.axis().scale(xScale)
      chart.append("g").style({'stroke': 'black', 'fill': 'none', 'stroke-width': '6px'}).attr("class", "xAxis").call(axis);
    
      d3.selectAll('g.tick').style('stroke-width', 0);

      // chart.append("line")
      //   .attr("x1", width/4-25).attr("x2", width/4-25)
      //   .attr("y1", 25).attr("y2", height)
      //   .style("stroke", "yellow")
      //   .style("stroke-width", '3px')
      //   .call(drag);

      // chart.append("line")
      //   .attr("x1", width/2-25).attr("x2", width/2-25)
      //   .attr("y1", 25).attr("y2", height)
      //   .style("stroke", "#D3D3D3")
      //   .style("stroke-width", '3px')

      // chart.append("line")
      //   .attr("x1", width*3/4-25).attr("x2", width*3/4-25)
      //   .attr("y1", 25).attr("y2", height)
      //   .style("stroke", "yellow")
      //   .style("stroke-width", '3px')
      //   .call(drag);

      // function zoom() {
      //   chart.select(".xAxis").call(axis);
        
      //   if(scale != d3.event.scale)
      //     beeswarm()
      //   scale = d3.event.scale

      //   chart.selectAll("circle.node")
      //     .transition(10)
      //     .attr("cx", function(d) { return xScale(d.x) })
      //     .attr("cy", dy)
      // }

      var nodes = chart.selectAll("circle.node")
        .data(data)
      
      beeswarm()

      nodes.enter().append("circle")
          .attr("class", "node")
          .attr("cx", function(d) { return xScale(d.x) })
          .attr("cy", dy)
          .attr("r", dr)
          .attr("fill", colorX)
          .style("stroke", "black")
          .style("stroke-width", 1)
          .on("mouseover", function(d) {
            tooltip.select(".system").html(d.system)
            return tooltip.select(".label").html(d.label)
          })
          .on("mouseout", function(d) {
            tooltip.select(".system").html("&nbsp;")
            return tooltip.select(".label").html("&nbsp;")
          })
          .on("click", function(d, i) {
            var inRange = function(dPrime, iPrime) {
              return Math.pow(i-iPrime, 2) <= 4
            }
          
            d3.selectAll("circle.node").filter(inRange).style("stroke", "yellow")
            d3.selectAll("circle.node").filter(function(dPrime, iPrime) { return !inRange(dPrime, iPrime) })
              .style("stroke", "black")
          })
      
      function beeswarm() {
        // reset vertical position
        data.map(function(d) {
          d.y = height / 2
        })
        for(var iter = 0; iter < 10; iter++) {
          var q = d3.geom.quadtree(data)
          for(var i = 0; i < data.length; i++)
            q.visit(collide(data[i]))
        }		
      }
        
      function collide(node) {
        var r = node.r + 16,
            nx1 = xScale(node.x) - r,
            nx2 = xScale(node.x) + r,
            ny1 = node.y - r,
            ny2 = node.y + r;
        return function(quad, x1, y1, x2, y2) {
          if (quad.point && (quad.point !== node)) {
            var x = xScale(node.x) - xScale(quad.point.x),
                y = node.y - quad.point.y,
                l = Math.sqrt(x * x + y * y),
                r = node.r + quad.point.r;
            if (l < r)
              node.y += norm()
          }
          return xScale(x1) > nx2
              || xScale(x2) < nx1
              || y1 > ny2
              || y2 < ny1	
        }
      }
    },
    InitSliders() {

      var svg = d3.select("#Sliders");
      svg.selectAll("*").remove();

      var width = 2525
      var height = 250

      var xScaleOp = d3.scale.linear()
        .domain([0, width-50])
        .range([0, 100])

      var activeClassName = 'active-d3-item';

      var svgLines = d3.select('#Sliders').append('svg');
      svgLines.attr('width', width);
      svgLines.attr('height', height);
      
      //The data for our lines and endpoints
      var data = [ 
        { 
          'id': 1,
          'x1': width/4+10,
          'y1': 25,
          'x2': width/4+10,
          'y2': height,
          'stroke': '#D3D3D3',
          'strokeW': '5px'
        }, 
        { 
          'id': 2,
          'x1': width/2,  
          'y1': 25,
          'x2': width/2,
          'y2': height,
          'stroke': 'black',
          'strokeW': '3px'
        },  
        { 
          'id': 3,
          'x1': width*3/4-12, 
          'y1': 25,
          'x2': width*3/4-12,
          'y2': height,
          'stroke': '#D3D3D3',
          'strokeW': '5px',
        }
      ];

      // Generating the svg lines attributes
      var lineAttributes = {
          'id': function(d) {
              return d.id;
          },
          'x1': function(d) {
              return d.x1;
          },
          'y1': function(d) {
              return d.y1;
          },
          'x2': function(d) {
              return d.x2;
          },
          'y2': function(d) {
              return d.y2;
          },
          'stroke': function(d) {
            return d.stroke
          },
          'stroke-width': function(d) {
            return d.strokeW
          }
      };
        
      var drag = d3.behavior.drag()
        .origin(function(d) { return d; })
        .on('dragstart', dragstarted)
        .on('drag', dragged)
        .on('dragend', dragended);

      // Pointer to the d3 lines
      var lines = svgLines
        .selectAll('line')
          .data(data)
        .enter()
          .append('line')
              .attr(lineAttributes)
              .call(drag);

      function dragstarted() {
        if (d3.select(this)[0][0].id == 2) {
          d3.select(this).classed(activeClassName, false);
        } else {
          d3.select(this).classed(activeClassName, true);
        }

      }

      function dragged() {
          var x = d3.event.dx;
          var y = d3.event.dy;

          var line = d3.select(this);
          var lineID = parseInt(line.attr('id'))
          if (lineID == 2) {
            var attributes = {
              x1: parseInt(line.attr('x1')),
              y1: parseInt(line.attr('y1')),

              x2: parseInt(line.attr('x2')),
              y2: parseInt(line.attr('y2')),
            };
          } else {
            var attributes = {
              x1: parseInt(line.attr('x1')) + x,
              y1: parseInt(line.attr('y1')),

              x2: parseInt(line.attr('x2')) + x,
              y2: parseInt(line.attr('y2')),
            };
          }
          if (lineID == 1) {
              if (attributes.x1 > 1125) {
                attributes.x1 = 1125
                attributes.x2 = 1125
                return line.attr(attributes);
              } else if (attributes.x1 < 125) {
                attributes.x1 = 125
                attributes.x2 = 125
                return line.attr(attributes);
              } else {
                return line.attr(attributes);
              }
          } else if (lineID == 3) {
              if (attributes.x1 > 2370) {
                attributes.x1 = 2370
                attributes.x2 = 2370
                return line.attr(attributes);
              } else if (attributes.x1 < 1370) {
                attributes.x1 = 1370
                attributes.x2 = 1370
                return line.attr(attributes);
              } else {
                return line.attr(attributes);
              }
          } else {
            return line.attr(attributes);
          }
            
        }

        function dragended() {
          if (d3.select(this)[0][0].getAttribute('id') == 3) {
            EventBus.$emit('SendtheChangeinRangePos', Math.floor(xScaleOp(d3.select(this)[0][0].x1.baseVal.value)))
          } else if (d3.select(this)[0][0].getAttribute('id') == 1) {
            EventBus.$emit('SendtheChangeinRangeNeg', Math.floor(xScaleOp(d3.select(this)[0][0].x1.baseVal.value)))
          } else {
            
          }
          d3.select(this).classed(activeClassName, false);
        }
    },
    updateSliders () {

      var svg = d3.select("#TextLabels");
      svg.selectAll("*").remove();

      var width = 2525
      var height = 250

      var svgLines = d3.select('#TextLabels').append('svg');
      svgLines.attr('width', width);
      svgLines.attr('height', height);

      if (this.rootIDSelected == 1) {
        svgLines
          .append("text")
          .attr("x", 0.5*width/4).attr("y", 248)
          .style("text-anchor", "middle")
          .style("font-size", "16px").text("Worst")
          .style("font-weight", "bold");

        svgLines
          .append("text")
          .attr("x", 1.5*width/4).attr("y", 248)
          .style("text-anchor", "middle")
          .style("font-size", "16px").text("Bad")
          .style("font-weight", "bold");

        svgLines
          .append("text")
          .attr("x", 2.5*width/4).attr("y", 248)
          .style("text-anchor", "middle")
          .style("font-size", "16px").text("Good")
          .style("font-weight", "bold");

        svgLines
          .append("text")
          .attr("x", 3.5*width/4).attr("y", 248)
          .style("text-anchor", "middle")
          .style("font-size", "16px").text("Best")
          .style("font-weight", "bold");

      } else if (this.rootIDSelected == 2) {
        svgLines
          .append("text")
          .attr("x", 0.5*width/4).attr("y", 248)
          .style("text-anchor", "middle")
          .style("font-size", "16px").text("Worst");

        svgLines
          .append("text")
          .attr("x", 1.5*width/4).attr("y", 248)
          .style("text-anchor", "middle")
          .style("font-size", "16px").text("Bad");

        svgLines
          .append("text")
          .attr("x", 2.5*width/4).attr("y", 248)
          .style("text-anchor", "middle")
          .style("font-size", "16px").text("Good");

        svgLines
          .append("text")
          .attr("x", 3.5*width/4).attr("y", 248)
          .style("text-anchor", "middle")
          .style("font-size", "16px").text("Best")
          .style("font-weight", "bold");

      } else if (this.rootIDSelected == 3) {
              svgLines
          .append("text")
          .attr("x", 0.5*width/4).attr("y", 248)
          .style("text-anchor", "middle")
          .style("font-size", "16px").text("Worst");

        svgLines
          .append("text")
          .attr("x", 1.5*width/4).attr("y", 248)
          .style("text-anchor", "middle")
          .style("font-size", "16px").text("Bad");

        svgLines
          .append("text")
          .attr("x", 2.5*width/4).attr("y", 248)
          .style("text-anchor", "middle")
          .style("font-size", "16px").text("Good")
          .style("font-weight", "bold");

        svgLines
          .append("text")
          .attr("x", 3.5*width/4).attr("y", 248)
          .style("text-anchor", "middle")
          .style("font-size", "16px").text("Best");
          
      } else if (this.rootIDSelected == 4) {
                svgLines
          .append("text")
          .attr("x", 0.5*width/4).attr("y", 248)
          .style("text-anchor", "middle")
          .style("font-size", "16px").text("Worst");

        svgLines
          .append("text")
          .attr("x", 1.5*width/4).attr("y", 248)
          .style("text-anchor", "middle")
          .style("font-size", "16px").text("Bad")
          .style("font-weight", "bold");

        svgLines
          .append("text")
          .attr("x", 2.5*width/4).attr("y", 248)
          .style("text-anchor", "middle")
          .style("font-size", "16px").text("Good");

        svgLines
          .append("text")
          .attr("x", 3.5*width/4).attr("y", 248)
          .style("text-anchor", "middle")
          .style("font-size", "16px").text("Best");
          
      } else {
        svgLines
          .append("text")
          .attr("x", 0.5*width/4).attr("y", 248)
          .style("text-anchor", "middle")
          .style("font-size", "16px").text("Worst")
          .style("font-weight", "bold");

        svgLines
          .append("text")
          .attr("x", 1.5*width/4).attr("y", 248)
          .style("text-anchor", "middle")
          .style("font-size", "16px").text("Bad");

        svgLines
          .append("text")
          .attr("x", 2.5*width/4).attr("y", 248)
          .style("text-anchor", "middle")
          .style("font-size", "16px").text("Good");

        svgLines
          .append("text")
          .attr("x", 3.5*width/4).attr("y", 248)
          .style("text-anchor", "middle")
          .style("font-size", "16px").text("Best");

      }
    },
    reset () {
      var svg = d3.select("#BeeSwarm");
      svg.selectAll("*").remove();
      var svg = d3.select("#Sliders");
      svg.selectAll("*").remove();
      this.status = true
    },
  },
  mounted () {
    EventBus.$on('keepRootFun', data => { this.rootIDSelected = data })
    EventBus.$on('keepRootFun', this.updateSliders)
    EventBus.$on('dataSpace', this.updateSliders)

    EventBus.$on('ConfirmDataSet', data => {this.status = false})

    EventBus.$on('SendtheChangeinRangePos', data => {this.PositiveValue = data})
    EventBus.$on('SendtheChangeinRangeNeg', data => {this.NegativeValue = data})
    EventBus.$on('dataSpace', data => { this.dataInstances = data })
    EventBus.$on('dataSpace', this.initializeBeeSwarm)
    EventBus.$on('SlidersCall', this.InitSliders)

    EventBus.$on('ConfirmDataSet', function () { 
      document.getElementById("NoAction").style.zIndex = "3";
    })

    EventBus.$on('reset', this.reset)
  }
}
</script>

<style>
 
text {
  font-family: sans-serif;
}

#AllClass { position: relative}
#BeeSwarm { position: absolute; top: 0; left: 0; z-index: 1;}
#Sliders { position: absolute; top: 0; left: 0; z-index: 2}
#NoAction { position: absolute; top: 0; left: 0; z-index: -1}
#TextLabels {position: absolute; top: 0; left: 0; z-index: 1}

.active-d3-item {
    cursor: pointer;
    stroke: yellow;
}
</style>