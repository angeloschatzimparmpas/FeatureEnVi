<template>
<div>
  <div id="HistoryPlot" ></div>
  <div id="LinePlot"></div>
</div>
</template>

<script>

import { EventBus } from '../main.js'
import * as Plotly from 'plotly.js'

export default {
  name: 'Results',
  data () {
    return {
      ValidResultsVar: [],
      globalStep: 0,
      featuresReceived: [],
      scoresMean: [],
      scoresSTD: [],
      scoresMeanBest: [],
      scoresSTDBest: [],
      xaxis: [],
      valuesGlobal: [], 
      historyKey: -1,
      whereIsChange: -1,
      previousState: [],
      storeBestSoFarAV: 0,
      flag: true,
      onHold: 0,
      keepFeaturesAddedGenRemoved: 0,
      whoCalls: true
    }
  },
  methods: {
    HistoryPun() {

      this.globalStep = this.globalStep + 1
      var state = this.globalStep
      if (state == 1) {
        this.storeBestSoFarAV = (parseFloat(this.scoresMean[0]) + parseFloat(this.scoresMean[1]) + parseFloat(this.scoresMean[2]) - parseFloat(this.scoresSTD[0]) - parseFloat(this.scoresSTD[1]) - parseFloat(this.scoresSTD[2]))
      } else {
        if (this.historyKey == 0 || this.historyKey == 1) {
          if (this.whoCalls) {
            this.globalStep = this.globalStep - 1
            state = this.globalStep
          }
        }
      }

      var svg = d3.select("#HistoryPlot");
      svg.selectAll("*").remove();

      var data = []
      var features = this.featuresReceived[33]
      
      if (this.historyKey == 5) {
        this.onHold = 0
      }
      if (this.historyKey == 3) {
        if (this.onHold > 0) {
          for ( var i = 0; i < this.onHold; i++ ) {
            features.pop();
          }
        }
      }

      if (this.historyKey == -1) {
        for (let i = 0; i < features.length; i++) {
            this.valuesGlobal.push([state,0,0,0])
        }
      } else if (this.historyKey == 0) {
        this.valuesGlobal[this.whereIsChange][this.historyKey] = state
      } else if (this.historyKey == 1) {
        this.valuesGlobal[this.whereIsChange][this.historyKey] = state
      } else if (this.historyKey == 2) {  
        this.valuesGlobal[this.whereIsChange][this.historyKey] = state
      } else if (this.historyKey == 3) {  
        for (let j = 0; j < this.whereIsChange.length; j++) {
          this.valuesGlobal[this.whereIsChange[j]][this.historyKey] = state
        }
      } else if (this.historyKey == 4) {  
        for (let j = 0; j < this.whereIsChange.length; j++) {
          this.valuesGlobal[this.whereIsChange[j]][0] = state
        }
      } else if (this.historyKey == 5) {
        for (let k = 0; k < this.keepFeaturesAddedGenRemoved ; k++) {
          this.valuesGlobal.push([state,0,0,0])
        }
      } else {

      }
      var toWhichTrans = this.historyKey
      //console.log(toWhichTrans)
      var toWhichPosition = this.whereIsChange
      //console.log(toWhichPosition)
      var counterSet = -1

      var labelsX = ['Include', 'Exclude', 'Transform', 'Generate']

      for (let i=0; i< features.length; i++) {
        data.push({
          label: features[i],
          values: this.valuesGlobal[i]
        })
      }
      
      if (data.length <= 7) {
        var heightFinal = 578
      } else {
        var heightFinal = data.length * 80
      }

      var margin = {top: 0, right: 0, bottom: 0, left: 0}
      var width = 390 - margin.left - margin.right
      var height = heightFinal - margin.top - margin.bottom
      var padding = 3
      var xLabelHeight = 30
      var yLabelWidth = 80
      var borderWidth = 0
      var duration = 50

      var chart = d3.select('#HistoryPlot').append('svg')
          .attr('width', width + margin.left + margin.right)
          .attr('height', height + margin.top + margin.bottom)
          .append('g')
          .attr('transform', 'translate(' + 0 + ',' + 0 + ')')

      var border = chart.append('rect')
          .attr('x', yLabelWidth)
          .attr('y', xLabelHeight)
          .style('fill-opacity', 0)
          .style('stroke', '#000')
          .style('stroke-width', borderWidth)
          .style('shape-rendering', 'crispEdges')

      //var color = JSON.parse(this.ValidResultsVar[12])


      var allValues = Array.prototype.concat.apply([], data.map(function(d) { return d.values }))
      var maxWidth = d3.max(data.map(function(d) { return d.values.length }))
      var maxR = d3.min([(width - yLabelWidth) / maxWidth, (height - xLabelHeight) / 5]) / 2 // Changed to 4 from data.length

      // var r = function(d) {

      //   var f = d3.scale.sqrt()
      //       .domain([d3.min(allValues), d3.max(allValues)])
      //       .rangeRound([0, maxR - padding])

      //   return f(d)
      // }

      var c = d3.scale.linear()
        .domain([d3.min(allValues), d3.max(allValues)])
        .rangeRound([255 * 0.8, 0])

      var rows = chart.selectAll('.row')
          .data(data, function(d){ return d.label })

      rows.enter().append('g')
          .attr('class', 'row')

      rows.exit()
          .transition()
          .duration(duration)
          .style('fill-opacity', 0)
          .remove()

      rows.transition()
          .duration(duration)
          .attr('transform', function(d, i){ return 'translate(' + yLabelWidth + ',' + (maxR * i * 2 + maxR + xLabelHeight) + ')' })

      var dots = rows.selectAll('circle')
          .data(function(d){ return d.values })

      dots.enter().append('circle')
          .attr('cy', 0)
          .attr('r', 0)
          .style('fill', '#ffffff')
          .text(function(d){ return d })

      dots.exit()
          .transition()
          .duration(duration)
          .attr('r', 0)
          .remove()

      if (this.whoCalls) {
        if (this.storeBestSoFarAV <= (parseFloat(this.scoresMean[0]) + parseFloat(this.scoresMean[1]) + parseFloat(this.scoresMean[2]) - parseFloat(this.scoresSTD[0]) - parseFloat(this.scoresSTD[1]) - parseFloat(this.scoresSTD[2]))) {
          this.flag = true
          this.storeBestSoFarAV = parseFloat(this.scoresMean[0]) + parseFloat(this.scoresMean[1]) + parseFloat(this.scoresMean[2]) - parseFloat(this.scoresSTD[0]) - parseFloat(this.scoresSTD[1]) - parseFloat(this.scoresSTD[2])
        }
      }

      var previously = this.previousState
      if (toWhichTrans == 5) {
        previously.push("black")
        previously.push("black")
        previously.push("black")
        previously.push("black")
      } 

      var lengthFeatures = this.valuesGlobal.length
      var testLoc = this.flag

      dots.transition()
          .duration(duration)
          .attr('r', function(d){ return d*2 })
          .attr('cx', function(d, i){ return i * maxR * 2 + maxR })
          .style('fill', function(d){
            counterSet = counterSet + 1 
            if (testLoc) {
              if (toWhichTrans == -1) {
                  previously.push("black") 
              }
              if (d == state) {
                previously[counterSet] = '#B15928'
                return previously[counterSet]
              } else if (toWhichTrans == 3 || toWhichTrans == 4) {
                var found = false
                for (let i = 0; i < toWhichPosition.length; i++) {
                  if (counterSet == (4*toWhichPosition[i] + 0) || counterSet == (4*toWhichPosition[i] + 1) || counterSet == (4*toWhichPosition[i] + 2) || counterSet == (4*toWhichPosition[i] + 3)) {
                    previously[counterSet] = 'black'
                    found = true
                    return previously[counterSet]
                  }
                }
                if (!found) {
                  return previously[counterSet]
                }
              } else if (counterSet == (4*toWhichPosition + 0) || counterSet == (4*toWhichPosition + 1) || counterSet == (4*toWhichPosition + 2) || counterSet == (4*toWhichPosition + 3)) {
                previously[counterSet] = 'black'
                return previously[counterSet]
              } else {
                return previously[counterSet]
              }
            } else {
              if (d == state) {
                previously[counterSet] = "black"
                return previously[counterSet]
              } else {
                return previously[counterSet]
              }
            }
          })

      this.whoCalls = false
      this.flag = false
      this.previousState = previously

      var dotLabels = rows.selectAll('.dot-label')
          .data(function(d){ return d.values })

      var dotLabelEnter = dotLabels.enter().append('g')
          .attr('class', 'dot-label')
          .on('mouseover', function(d){
              var selection = d3.select(this)
              selection.select('rect').transition().duration(100).style('opacity', 1)
              selection.select("text").transition().duration(100).style('opacity', 1)
          })
          .on('mouseout', function(d){
              var selection = d3.select(this)
              selection.select('rect').transition().style('opacity', 0)
              selection.select("text").transition().style('opacity', 0)
          })

      dotLabelEnter.append('rect')
          .style('fill', '#000000')
          .style('opacity', 0)

      dotLabelEnter.append('text')
          .style('text-anchor', 'middle')
          .style('fill', '#ffffff')
          .style('opacity', 0)

      dotLabels.exit().remove()

      dotLabels
          .attr('transform', function(d, i){ return 'translate(' + (i * maxR * 2) + ',' + (-maxR) + ')' })
          .select('text')
              .text(function(d){ return 'Step: '+d })
              .attr('y', maxR + 4)
              .attr('x', maxR)

      dotLabels
          .select('rect')
          .attr('width', maxR * 2)
          .attr('height', maxR * 2)

      var xLabels = chart.selectAll('.xLabel')
          .data(labelsX)

      xLabels.enter().append('text')
          .attr('y', xLabelHeight)
          .attr('transform', 'translate(0,-6)')
          .attr('class', 'xLabel')
          .style("font-size", "14px")
          .style('text-anchor', 'middle')
          .style('fill-opacity', 0)

      xLabels.exit()
          .transition()
          .duration(duration)
          .style('fill-opacity', 0)
          .remove()

      xLabels.transition()
          .text(function (d) { return d })
          .duration(duration)
          .attr('x', function(d, i){ return maxR * i * 2 + maxR + yLabelWidth - 2})
          .style('fill-opacity', 1)

      var yLabels = chart.selectAll('.yLabel')
          .data(data, function(d){ return d.label })

      yLabels.enter().append('text')
          .text(function (d) { return d.label })
          .attr('x', yLabelWidth)
          .attr('class', 'yLabel')
          .style("font-size", "14px")
          .style('text-anchor', 'end')
          .style('fill-opacity', 0)

      yLabels.exit()
          .transition()
          .duration(duration)
          .style('fill-opacity', 0)
          .remove()

      yLabels.transition()
          .duration(duration)
          .attr('y', function(d, i){ return maxR * i * 2 + maxR + xLabelHeight - 9 })
          .attr('transform', 'translate(-6,' + maxR / 2.5 + ')')
          .style('fill-opacity', 1)

      var vert = chart.selectAll('.vert')
          .data(labelsX)

      vert.enter().append('line')
          .attr('class', 'vert')
          .attr('y1', xLabelHeight + borderWidth / 2)
          .attr('stroke', '#888')
          .attr('stroke-width', 1)
          .style('shape-rendering', 'crispEdges')
          .style('stroke-opacity', 0)

      vert.exit()
          .transition()
          .duration(duration)
          .style('stroke-opacity', 0)
          .remove()

      vert.transition()
          .duration(duration)
          .attr('x1', function(d, i){ return maxR * i * 2 + yLabelWidth })
          .attr('x2', function(d, i){ return maxR * i * 2 + yLabelWidth })
          .attr('y2', maxR * 2 * data.length + xLabelHeight - borderWidth / 2)
          .style('stroke-opacity', function(d, i){ return i ? 1 : 0 })

      var horiz = chart.selectAll('.horiz').
          data(data, function(d){ return d.label })

      horiz.enter().append('line')
          .attr('class', 'horiz')
          .attr('x1', yLabelWidth + borderWidth / 2)
          .attr('stroke', '#888')
          .attr('stroke-width', 1)
          .style('shape-rendering', 'crispEdges')
          .style('stroke-opacity', 0)

      horiz.exit()
          .transition()
          .duration(duration)
          .style('stroke-opacity', 0)
          .remove()

      horiz.transition()
          .duration(duration)
          .attr('x2', maxR * 2 * labelsX.length + yLabelWidth - borderWidth / 2)
          .attr('y1', function(d, i){ return i * maxR * 2 + xLabelHeight })
          .attr('y2', function(d, i){ return i * maxR * 2 + xLabelHeight })
          .style('stroke-opacity', function(d, i){ return i ? 1 : 0 })

      border.transition()
          .duration(duration)
          .attr('width', maxR * 2 * labelsX.length)
          .attr('height', maxR * 2 * data.length)
    },
    initializeLinePLot () { 

      Plotly.purge('LinePlot')
      this.scoresMean = []
      this.scoresSTD = []
      this.scoresMeanBest = []
      this.scoresSTDBest = []

      this.xaxis.push('Accuracy') 
      this.xaxis.push('Precision') 
      this.xaxis.push('Recall') 

      this.scoresMean.push((JSON.parse(this.ValidResultsVar[0])*100).toFixed(2))
      this.scoresSTD.push((JSON.parse(this.ValidResultsVar[1])*100).toFixed(2))
      this.scoresMean.push((JSON.parse(this.ValidResultsVar[2])*100).toFixed(2))
      this.scoresSTD.push((JSON.parse(this.ValidResultsVar[3])*100).toFixed(2))
      this.scoresMean.push((JSON.parse(this.ValidResultsVar[4])*100).toFixed(2))
      this.scoresSTD.push((JSON.parse(this.ValidResultsVar[5])*100).toFixed(2))

      this.scoresMeanBest.push((JSON.parse(this.ValidResultsVar[6])*100).toFixed(2))
      this.scoresSTDBest.push((JSON.parse(this.ValidResultsVar[7])*100).toFixed(2))
      this.scoresMeanBest.push((JSON.parse(this.ValidResultsVar[8])*100).toFixed(2))
      this.scoresSTDBest.push((JSON.parse(this.ValidResultsVar[9])*100).toFixed(2))
      this.scoresMeanBest.push((JSON.parse(this.ValidResultsVar[10])*100).toFixed(2))
      this.scoresSTDBest.push((JSON.parse(this.ValidResultsVar[11])*100).toFixed(2))   

      var trace1 = {
        x: this.xaxis, 
        y: this.scoresMean, 
        error_y: {
          type: 'data',
          array: this.scoresSTD,
          visible: true
        },
        marker: {
          color: "rgb(64,224,208)"
        },
        name: "Current",
        type: "bar",
      }

      var trace2 = {
        x: this.xaxis, 
        y: this.scoresMeanBest, 
        error_y: {
          type: 'data',
          array: this.scoresSTDBest,
          visible: true
        },
        marker: {
          color: "rgb(177,89,40)"
        },
        name: "Best", 
        type: "bar"
      }

      var DataforLinePlot = [trace1, trace2];

      var layout = {
        xaxis: {
            gridcolor: "rgb(230,230,230)",
            title: 'Validation metric',
            tickformat: '.0f',
            font: {
              size: 13,
              color: '#000000'
            },
            showgrid: true, 
            showline: false, 
            showticklabels: true, 
            tickcolor: "rgb(230,230,230)", 
            ticks: "outside", 
            zeroline: false
        }, 
        yaxis: {
            gridcolor: "rgb(230,230,230)", 
            title: 'Performance (%)',
            font: {
              size: 13,
              color: '#000000'
            },
            showgrid: true, 
            showline: false, 
            showticklabels: true, 
            tickcolor: "rgb(230,230,230)", 
            ticks: "outside", 
            zeroline: false
        },
        barmode: 'group',
        autosize: false,
        width: '395',
        height: '300',
        margin: {
          l: 55,
          r: 5,
          b: 50,
          t: 5,
          pad: 5
        },
        font: {
              size: 13,
              color: '#000000'
        },
        legend:{
          xanchor:"center",
          yanchor:"top",
          font: {
              size: 13,
              color: '#000000'
          },
          y:-0.35, // play with it
          x:0.5,   // play with it
          orientation: "h"
        }
      }
      var config = {displayModeBar: false, scrollZoom: true, displaylogo: false, showLink: false, showSendToCloud: false, modeBarButtonsToRemove: ['toImage'], responsive: true}
      Plotly.newPlot('LinePlot', DataforLinePlot, layout, config)
      
    },
    reset () {
      var svg = d3.select("#HistoryPlot");
      svg.selectAll("*").remove();
      Plotly.purge('LinePlot')
    },
  },
  mounted () {

    EventBus.$on('updateHistoryKey', data => { this.historyKey = data })
    EventBus.$on('updateValuesofHistory', data => { this.whereIsChange = data })

    EventBus.$on('addFeatureGen', data => { this.onHold = Object.values(data).length })

    EventBus.$on('finalResults', data => { this.ValidResultsVar = data })
    EventBus.$on('finalResults', this.initializeLinePLot)
    
    EventBus.$on('quad', data => { this.featuresReceived = data })
    EventBus.$on('HistoryCalled', data => { this.whoCalls = data })
    EventBus.$on('HistoryCalled', this.HistoryPun)

    EventBus.$on('addFeatureGen', data => { this.keepFeaturesAddedGenRemoved = Object.values(data).length })

    EventBus.$on('reset', this.reset)
  }
}
</script>

<style>

text {
  font-family: sans-serif;
  fill: black;
  cursor: default;
}

svg {
  display: block;
}

.nodeHighlighted {
  stroke: 'orange'
}

.modebar{
  display: none !important;
}

body {
  background-color: #fff;
}

.dot-label text {
  font-size: 12px;
}

div#HistoryPlot {
  height: 578px;
  overflow: scroll;
}

</style>