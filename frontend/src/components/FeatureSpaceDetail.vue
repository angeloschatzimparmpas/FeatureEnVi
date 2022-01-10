<template>
  <div class="column">
    <svg id="chartID" class="chart" style="min-height: 66px !important; max-height: 66px !important; min-width:318px !important;"></svg>
    <div id="FeatureGraph" style="border-style: solid; border-width: 3px; border-color: black; min-height: 819px; max-height: 819px; min-width: 819px !important; max-width: 819px !important"></div> 
      <div id="toolbar" style="min-height: 67px; max-height: 67px; margin-top: 25px; max-width: 819px !important">
          <div class="panel panel-default" data-placement="center">
            <div class="panel-body" id="resetAllFilters" data-placement="center" style="margin-top: -20px">
              <table class="table table-borderless centerTable" >
                <tbody>
                  <tr>
                    <div style="border: 1px solid black; height:68px; margin-top:19px">
                    <td scope="row"><button class="btn btn-primary active" id="initButton" v-on:click="setLayerExplore" style="margin-top: 3px; margin-left: 0px !important" ><font-awesome-icon icon="wrench" style="margin-right: 5px"/>Feature Transformation</button></td>
                    <td><button class="btn btn-primary" v-on:click="setLayerCompare" style="margin-top: 3px; margin-left: -15px"><font-awesome-icon icon="balance-scale" style="margin-right: 5px" />Feature Generation</button></td>
                    </div>
                    <td>
                      <div id="glyphLegend">
                      <div id="buildLegend">
                      <div id="legend" style="margin-top: 2px; margin-left: -6px"></div>
                      <div id="legendText" title="MI: Mutual Information (range: light blue to dark blue); COR: Correlation (range: 0%-100%); VIF: Variance Influence Factor (range: ... < 2.5 < 5 < 10 < ...)" style="border: 1px solid black; min-height: 68px; max-height: 68px; min-width:170px; margin-top: 17px; margin-left: -12px"></div>
                      </div>
                      </div>
                    </td>
                    <td>
                      <div id="floatingPanel" class="row align-items-center " style="height: 66px; margin-top:11px; border: 1px solid black; max-width: 260px">
                        <div class="col-lg-4" style="margin-top:3px; margin-left: -5px"><p>Fs COR (>)</p></div>
                        <div class="col-lg-7" style="margin-top:1px; margin-left: -15px"><div id="thres"></div></div>
                      </div>
                    </td> 
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
      </div>
  </div>
</template>

<script>
import { EventBus } from '../main.js'
import * as greadability from '../greadability.js'
import * as d3Base from 'd3'
import $ from 'jquery'

// attach all d3 plugins to the d3 library
const d3 = Object.assign(d3Base)

export default {
  name: 'FeatureSpaceDetail',
  data () {
    return {
      dataFS: [],
      legendOnlyOnce: true,
      dataFSTrans: [],
      quadrantNumber: 4,
      threshold: 0.4,
      jsonData: [],
      corrMatrixComb: [],
      corrMatrixCombTotal: [],
      VIFRemaining: [],
      MIRemaining: [],
      featureAddRemCount: [],
      mode: 0, // this should be 0
      KeepIDs: [],
      KeepIDTransform: [],
      KeepNamesGlobal: [],
      keepNumberOfCompareNodes: 0,
      activeLeafNode: -1,
      spaceChangeDetail: false
    }
  },
  methods: {
      InitSlider () {  
      var dataCorrect = [0, 0.2, 0.4, 0.6, 0.8, 1];

        var sliderStepPos = d3
          .sliderBottom()
          .min(d3.min(dataCorrect))
          .max(d3.max(dataCorrect))
          .width(150)
          .tickFormat(d3.format(".1f"))
          .ticks(6)
          .step(0.2)
          .default(0.4)
          .on('onchange', val => {
            EventBus.$emit('CorrThres', d3.format(".1f")(val))
          });

        var gStepPos = d3
          .select('div#thres')
          .append('svg')
          .attr('width', 176)
          .attr('height', 80)
          .append('g')
          .attr('transform', 'translate(15,15)');

        gStepPos.call(sliderStepPos);

    },
    setLayerExplore() {
      this.mode = 0
      this.KeepIDs = []
      this.KeepNamesGlobal = []
      this.KeepIDTransform = []
      this.keepNumberOfCompareNodes = 0
      //this.graphVizualization()
      if(!this.spaceChangeDetail) {
        EventBus.$emit('storeGeneration')
      }
      this.spaceChangeDetail = false
    },
    setLayerCompare() {
      this.mode = 1 
      this.KeepIDTransform = []
      EventBus.$emit('brushLink', -1)
      this.graphVizualization()
    },
    computeOnce () {  
        var numberOfTransformations = 12 // change that
        
        var listofNodes = this.dataFS[34]
        var dataLocOnce = []
        for (let loop=1; loop<=5; loop++) {
          dataLocOnce.push(JSON.parse(this.dataFS[loop+2]))
        }

        var corrMatrixCombTotalLocGather = []
        var MIRemainingLocGather = []

        var featureNames = JSON.parse(this.dataFS[35])
        var pushEach
        var oldVal
        var newVal
        var outcome
        var countLoc
        var pushEachFinalFinal = []

        for (let loop=1; loop<=5; loop++) {
          var corrMatrixCombLoc =[]
          var corrMatrixCombTotalLoc = []
          var VIFRemainingLoc = []
          var MIRemainingLoc = []
          var pushEachFinal = []
          var quadrantNumberLocal = loop - 1

          this.dataFSTrans.forEach(function(element, index) {
              var transf1 = element.transf1
              corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf1[10+quadrantNumberLocal]))[0] * 100)
              MIRemainingLoc.push(JSON.parse(transf1[20+quadrantNumberLocal]))
              transf1 = JSON.parse(transf1[loop-1])
              oldVal = 0
              newVal = 0
              outcome = 0
              countLoc = 0
              pushEach = []
              Object.entries(transf1).forEach(
              function ([feature, value]) {
                var key = listofNodes[index]
                var retrieveData = dataLocOnce[loop-1]
                var search = Object.values(retrieveData[key])
                oldVal = Math.abs(search[countLoc]) + oldVal
                newVal = Math.abs(Object.values(value)[0]) + newVal
                countLoc++
              })
              oldVal = oldVal / listofNodes.length
              newVal = newVal / listofNodes.length
              outcome = oldVal - newVal
              pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+0], valueIns: outcome})

              var transf2 = element.transf2
              corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf2[10+quadrantNumberLocal]))[0] * 100)
              MIRemainingLoc.push(JSON.parse(transf2[20+quadrantNumberLocal]))
              transf2 = JSON.parse(transf2[loop-1])
              oldVal = 0
              newVal = 0
              outcome = 0
              countLoc = 0
              Object.entries(transf2).forEach(
              function ([feature, value]) {
                var key = listofNodes[index]
                var retrieveData = dataLocOnce[loop-1]
                var search = Object.values(retrieveData[key])
                oldVal = Math.abs(search[countLoc]) + oldVal
                newVal = Math.abs(Object.values(value)[0]) + newVal
                countLoc++
              })
              oldVal = oldVal / listofNodes.length
              newVal = newVal / listofNodes.length
              outcome = oldVal - newVal
              pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+1], valueIns: outcome})

              var transf3 = element.transf3
              corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf3[10+quadrantNumberLocal]))[0] * 100)
              MIRemainingLoc.push(JSON.parse(transf3[20+quadrantNumberLocal]))
              transf3 = JSON.parse(transf3[loop-1])
              oldVal = 0
              newVal = 0
              outcome = 0
              countLoc = 0
              Object.entries(transf3).forEach(
              function ([feature, value]) {
                var key = listofNodes[index]
                var retrieveData = dataLocOnce[loop-1]
                var search = Object.values(retrieveData[key])
                oldVal = Math.abs(search[countLoc]) + oldVal
                newVal = Math.abs(Object.values(value)[0]) + newVal
                countLoc++
              })
              oldVal = oldVal / listofNodes.length
              newVal = newVal / listofNodes.length
              outcome = oldVal - newVal
              pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+2], valueIns: outcome})

              var transf4 = element.transf4
              corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf4[10+quadrantNumberLocal]))[0] * 100)
              MIRemainingLoc.push(JSON.parse(transf4[20+quadrantNumberLocal]))
              transf4 = JSON.parse(transf4[loop-1])
              oldVal = 0
              newVal = 0
              outcome = 0
              countLoc = 0
              Object.entries(transf4).forEach(
              function ([feature, value]) {
                var key = listofNodes[index]
                var retrieveData = dataLocOnce[loop-1]
                var search = Object.values(retrieveData[key])
                oldVal = Math.abs(search[countLoc]) + oldVal
                newVal = Math.abs(Object.values(value)[0]) + newVal
                countLoc++
              })
              oldVal = oldVal / listofNodes.length
              newVal = newVal / listofNodes.length
              outcome = oldVal - newVal
              pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+3], valueIns: outcome})

              var transf5 = element.transf5
              corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf5[10+quadrantNumberLocal]))[0] * 100)
              MIRemainingLoc.push(JSON.parse(transf5[20+quadrantNumberLocal]))
              transf5 = JSON.parse(transf5[loop-1])
              oldVal = 0
              newVal = 0
              outcome = 0
              countLoc = 0
              Object.entries(transf5).forEach(
              function ([feature, value]) {
                var key = listofNodes[index]
                var retrieveData = dataLocOnce[loop-1]
                var search = Object.values(retrieveData[key])
                oldVal = Math.abs(search[countLoc]) + oldVal
                newVal = Math.abs(Object.values(value)[0]) + newVal
                countLoc++
              })
              oldVal = oldVal / listofNodes.length
              newVal = newVal / listofNodes.length
              outcome = oldVal - newVal
              pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+4], valueIns: outcome})
              

              var transf6 = element.transf6
              corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf6[10+quadrantNumberLocal]))[0] * 100)
              MIRemainingLoc.push(JSON.parse(transf6[20+quadrantNumberLocal]))
              transf6 = JSON.parse(transf6[loop-1])
              oldVal = 0
              newVal = 0
              outcome = 0
              countLoc = 0
              Object.entries(transf6).forEach(
              function ([feature, value]) {
                var key = listofNodes[index]
                var retrieveData = dataLocOnce[loop-1]
                var search = Object.values(retrieveData[key])
                oldVal = Math.abs(search[countLoc]) + oldVal
                newVal = Math.abs(Object.values(value)[0]) + newVal
                countLoc++
              })
              oldVal = oldVal / listofNodes.length
              newVal = newVal / listofNodes.length
              outcome = oldVal - newVal
              pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+5], valueIns: outcome})
              

              var transf7 = element.transf7
              corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf7[10+quadrantNumberLocal]))[0] * 100)
              MIRemainingLoc.push(JSON.parse(transf7[20+quadrantNumberLocal]))
              transf7 = JSON.parse(transf7[loop-1])
              oldVal = 0
              newVal = 0
              outcome = 0
              countLoc = 0
              Object.entries(transf7).forEach(
              function ([feature, value]) {
                var key = listofNodes[index]
                var retrieveData = dataLocOnce[loop-1]
                var search = Object.values(retrieveData[key])
                oldVal = Math.abs(search[countLoc]) + oldVal
                newVal = Math.abs(Object.values(value)[0]) + newVal
                countLoc++
              })
              oldVal = oldVal / listofNodes.length
              newVal = newVal / listofNodes.length
              outcome = oldVal - newVal
              pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+6], valueIns: outcome})
              

              var transf8 = element.transf8
              corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf8[10+quadrantNumberLocal]))[0] * 100)
              MIRemainingLoc.push(JSON.parse(transf8[20+quadrantNumberLocal]))
              transf8 = JSON.parse(transf8[loop-1])
              oldVal = 0
              newVal = 0
              outcome = 0
              countLoc = 0
              Object.entries(transf8).forEach(
              function ([feature, value]) {
                var key = listofNodes[index]
                var retrieveData = dataLocOnce[loop-1]
                var search = Object.values(retrieveData[key])
                oldVal = Math.abs(search[countLoc]) + oldVal
                newVal = Math.abs(Object.values(value)[0]) + newVal
                countLoc++
              })
              oldVal = oldVal / listofNodes.length
              newVal = newVal / listofNodes.length
              outcome = oldVal - newVal
              pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+7], valueIns: outcome})
              

              var transf9 = element.transf9
              corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf9[10+quadrantNumberLocal]))[0] * 100)
              MIRemainingLoc.push(JSON.parse(transf9[20+quadrantNumberLocal]))
              transf9 = JSON.parse(transf9[loop-1])
              oldVal = 0
              newVal = 0
              outcome = 0
              countLoc = 0
              Object.entries(transf9).forEach(
              function ([feature, value]) {
                var key = listofNodes[index]
                var retrieveData = dataLocOnce[loop-1]
                var search = Object.values(retrieveData[key])
                oldVal = Math.abs(search[countLoc]) + oldVal
                newVal = Math.abs(Object.values(value)[0]) + newVal
                countLoc++
              })
              oldVal = oldVal / listofNodes.length
              newVal = newVal / listofNodes.length
              outcome = oldVal - newVal
              pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+8], valueIns: outcome})
              

              var transf10 = element.transf10
              corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf10[10+quadrantNumberLocal]))[0] * 100)
              MIRemainingLoc.push(JSON.parse(transf10[20+quadrantNumberLocal]))
              transf10 = JSON.parse(transf10[loop-1])
              oldVal = 0
              newVal = 0
              outcome = 0
              countLoc = 0
              Object.entries(transf10).forEach(
              function ([feature, value]) {
                var key = listofNodes[index]
                var retrieveData = dataLocOnce[loop-1]
                var search = Object.values(retrieveData[key])
                oldVal = Math.abs(search[countLoc]) + oldVal
                newVal = Math.abs(Object.values(value)[0]) + newVal
                countLoc++
              })
              oldVal = oldVal / listofNodes.length
              newVal = newVal / listofNodes.length
              outcome = oldVal - newVal
              pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+9], valueIns: outcome})
              

              var transf11 = element.transf11
              corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf11[10+quadrantNumberLocal]))[0] * 100)
              MIRemainingLoc.push(JSON.parse(transf11[20+quadrantNumberLocal]))
              transf11 = JSON.parse(transf11[loop-1])
              oldVal = 0
              newVal = 0
              outcome = 0
              countLoc = 0
              Object.entries(transf11).forEach(
              function ([feature, value]) {
                var key = listofNodes[index]
                var retrieveData = dataLocOnce[loop-1]
                var search = Object.values(retrieveData[key])
                oldVal = Math.abs(search[countLoc]) + oldVal
                newVal = Math.abs(Object.values(value)[0]) + newVal
                countLoc++
              })
              oldVal = oldVal / listofNodes.length
              newVal = newVal / listofNodes.length
              outcome = oldVal - newVal
              pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+10], valueIns: outcome})
              
              
              var transf12 = element.transf12
              corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf12[10+quadrantNumberLocal]))[0] * 100)
              MIRemainingLoc.push(JSON.parse(transf12[20+quadrantNumberLocal]))
              transf12 = JSON.parse(transf12[loop-1])
              oldVal = 0
              newVal = 0
              outcome = 0
              countLoc = 0
              Object.entries(transf12).forEach(
              function ([feature, value]) {
                var key = listofNodes[index]
                var retrieveData = dataLocOnce[loop-1]
                var search = Object.values(retrieveData[key])
                oldVal = Math.abs(search[countLoc]) + oldVal
                newVal = Math.abs(Object.values(value)[0]) + newVal
                countLoc++
              })
              oldVal = oldVal / listofNodes.length
              newVal = newVal / listofNodes.length
              outcome = oldVal - newVal
              pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+11], valueIns: outcome})

              pushEachFinal.push({key: listofNodes[index], value: pushEach})
            })
            pushEachFinalFinal.push(pushEachFinal)
            corrMatrixCombTotalLocGather.push(corrMatrixCombTotalLoc)
            MIRemainingLocGather.push(MIRemainingLoc)
          }

        EventBus.$emit('overviewCallCorrTotal', corrMatrixCombTotalLocGather)
        EventBus.$emit('overviewCallMI', MIRemainingLocGather)
        EventBus.$emit('overviewCall', pushEachFinalFinal)

      },
      initializeNetwork () {   
        var numberOfTransformations = 12 // change that

        var featureNames = JSON.parse(this.dataFS[35])

        this.jsonData = []
        var threshLoc = this.threshold

        this.corrMatrixComb = [] 
        this.corrMatrixCombTotal = []
        this.VIFRemaining = []
        this.MIRemaining = []

        var quadrantNumberLocal = this.quadrantNumber
        var listofNodes = this.dataFS[34]
        var dataLoc = JSON.parse(this.dataFS[3+quadrantNumberLocal])

        var pushEachFinal = []
        var pushEach
        var oldVal
        var newVal
        var outcome
        var countLoc

        var corrMatrixCombLoc =[]
        var corrMatrixCombTotalLoc = []
        var VIFRemainingLoc = []
        var MIRemainingLoc = []

        this.dataFSTrans.forEach(function(element, index) {
          var transf1 = element.transf1
          corrMatrixCombLoc.push(Object.values(JSON.parse(transf1[5+quadrantNumberLocal])))
          corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf1[10+quadrantNumberLocal]))[0] * 100)
          VIFRemainingLoc.push(Object.values(JSON.parse(transf1[15+quadrantNumberLocal]))[0])
          MIRemainingLoc.push(JSON.parse(transf1[20+quadrantNumberLocal]))
          transf1 = JSON.parse(transf1[quadrantNumberLocal])
          oldVal = 0
          newVal = 0
          outcome = 0
          countLoc = 0
          pushEach = []
          Object.entries(transf1).forEach(
          function ([feature, value]) {
            var key = listofNodes[index]
            var search = Object.values(dataLoc[key])
            oldVal = Math.abs(search[countLoc]) + oldVal
            newVal = Math.abs(Object.values(value)[0]) + newVal
            countLoc++
          })
          oldVal = oldVal / listofNodes.length
          newVal = newVal / listofNodes.length
          outcome = oldVal - newVal
          pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+0], valueIns: outcome})


          var transf2 = element.transf2
          corrMatrixCombLoc.push(Object.values(JSON.parse(transf2[5+quadrantNumberLocal])))
          corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf2[10+quadrantNumberLocal]))[0] * 100)
          VIFRemainingLoc.push(Object.values(JSON.parse(transf2[15+quadrantNumberLocal]))[0])
          MIRemainingLoc.push(JSON.parse(transf2[20+quadrantNumberLocal]))
          transf2 = JSON.parse(transf2[quadrantNumberLocal])
          oldVal = 0
          newVal = 0
          outcome = 0
          countLoc = 0
          Object.entries(transf2).forEach(
          function ([feature, value]) {
            var key = listofNodes[index]
            var search = Object.values(dataLoc[key])
            oldVal = Math.abs(search[countLoc]) + oldVal
            newVal = Math.abs(Object.values(value)[0]) + newVal
            countLoc++
          })
          oldVal = oldVal / listofNodes.length
          newVal = newVal / listofNodes.length
          outcome = oldVal - newVal
          pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+1], valueIns: outcome})

          var transf3 = element.transf3
          corrMatrixCombLoc.push(Object.values(JSON.parse(transf3[5+quadrantNumberLocal])))
          corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf3[10+quadrantNumberLocal]))[0] * 100)
          VIFRemainingLoc.push(Object.values(JSON.parse(transf3[15+quadrantNumberLocal]))[0])
          MIRemainingLoc.push(JSON.parse(transf3[20+quadrantNumberLocal]))
          transf3 = JSON.parse(transf3[quadrantNumberLocal])
          oldVal = 0
          newVal = 0
          outcome = 0
          countLoc = 0
          Object.entries(transf3).forEach(
          function ([feature, value]) {
            var key = listofNodes[index]
            var search = Object.values(dataLoc[key])
            oldVal = Math.abs(search[countLoc]) + oldVal
            newVal = Math.abs(Object.values(value)[0]) + newVal
            countLoc++
          })
          oldVal = oldVal / listofNodes.length
          newVal = newVal / listofNodes.length
          outcome = oldVal - newVal
          pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+2], valueIns: outcome})

          var transf4 = element.transf4
          corrMatrixCombLoc.push(Object.values(JSON.parse(transf4[5+quadrantNumberLocal])))
          corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf4[10+quadrantNumberLocal]))[0] * 100)
          VIFRemainingLoc.push(Object.values(JSON.parse(transf4[15+quadrantNumberLocal]))[0])
          MIRemainingLoc.push(JSON.parse(transf4[20+quadrantNumberLocal]))
          transf4 = JSON.parse(transf4[quadrantNumberLocal])
          oldVal = 0
          newVal = 0
          outcome = 0
          countLoc = 0
          Object.entries(transf4).forEach(
          function ([feature, value]) {
            var key = listofNodes[index]
            var search = Object.values(dataLoc[key])
            oldVal = Math.abs(search[countLoc]) + oldVal
            newVal = Math.abs(Object.values(value)[0]) + newVal
            countLoc++
          })
          oldVal = oldVal / listofNodes.length
          newVal = newVal / listofNodes.length
          outcome = oldVal - newVal
          pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+3], valueIns: outcome})

          var transf5 = element.transf5
          corrMatrixCombLoc.push(Object.values(JSON.parse(transf5[5+quadrantNumberLocal])))
          corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf5[10+quadrantNumberLocal]))[0] * 100)
          VIFRemainingLoc.push(Object.values(JSON.parse(transf5[15+quadrantNumberLocal]))[0])
          MIRemainingLoc.push(JSON.parse(transf5[20+quadrantNumberLocal]))
          transf5 = JSON.parse(transf5[quadrantNumberLocal])
          oldVal = 0
          newVal = 0
          outcome = 0
          countLoc = 0
          Object.entries(transf5).forEach(
          function ([feature, value]) {
            var key = listofNodes[index]
            var search = Object.values(dataLoc[key])
            oldVal = Math.abs(search[countLoc]) + oldVal
            newVal = Math.abs(Object.values(value)[0]) + newVal
            countLoc++
          })
          oldVal = oldVal / listofNodes.length
          newVal = newVal / listofNodes.length
          outcome = oldVal - newVal
          pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+4], valueIns: outcome}) 
 
          var transf6 = element.transf6
          corrMatrixCombLoc.push(Object.values(JSON.parse(transf6[5+quadrantNumberLocal])))
          corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf6[10+quadrantNumberLocal]))[0] * 100)
          VIFRemainingLoc.push(Object.values(JSON.parse(transf6[15+quadrantNumberLocal]))[0])
          MIRemainingLoc.push(JSON.parse(transf6[20+quadrantNumberLocal]))
          transf6 = JSON.parse(transf6[quadrantNumberLocal])
          oldVal = 0
          newVal = 0
          outcome = 0
          countLoc = 0
          Object.entries(transf6).forEach(
          function ([feature, value]) {
            var key = listofNodes[index]
            var search = Object.values(dataLoc[key])
            oldVal = Math.abs(search[countLoc]) + oldVal
            newVal = Math.abs(Object.values(value)[0]) + newVal
            countLoc++
          })
          oldVal = oldVal / listofNodes.length
          newVal = newVal / listofNodes.length
          outcome = oldVal - newVal
          pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+5], valueIns: outcome})

          var transf7 = element.transf7
          corrMatrixCombLoc.push(Object.values(JSON.parse(transf7[5+quadrantNumberLocal])))
          corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf7[10+quadrantNumberLocal]))[0] * 100)
          VIFRemainingLoc.push(Object.values(JSON.parse(transf7[15+quadrantNumberLocal]))[0])
          MIRemainingLoc.push(JSON.parse(transf7[20+quadrantNumberLocal]))
          transf7 = JSON.parse(transf7[quadrantNumberLocal])
          oldVal = 0
          newVal = 0
          outcome = 0
          countLoc = 0
          Object.entries(transf7).forEach(
          function ([feature, value]) {
            var key = listofNodes[index]
            var search = Object.values(dataLoc[key])
            oldVal = Math.abs(search[countLoc]) + oldVal
            newVal = Math.abs(Object.values(value)[0]) + newVal
            countLoc++
          })
          oldVal = oldVal / listofNodes.length
          newVal = newVal / listofNodes.length
          outcome = oldVal - newVal
          pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+6], valueIns: outcome})
          
          var transf8 = element.transf8
          corrMatrixCombLoc.push(Object.values(JSON.parse(transf8[5+quadrantNumberLocal])))
          corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf8[10+quadrantNumberLocal]))[0] * 100)
          VIFRemainingLoc.push(Object.values(JSON.parse(transf8[15+quadrantNumberLocal]))[0])
          MIRemainingLoc.push(JSON.parse(transf8[20+quadrantNumberLocal]))
          transf8 = JSON.parse(transf8[quadrantNumberLocal])
          oldVal = 0
          newVal = 0
          outcome = 0
          countLoc = 0
          Object.entries(transf8).forEach(
          function ([feature, value]) {
            var key = listofNodes[index]
            var search = Object.values(dataLoc[key])
            oldVal = Math.abs(search[countLoc]) + oldVal
            newVal = Math.abs(Object.values(value)[0]) + newVal
            countLoc++
          })
          oldVal = oldVal / listofNodes.length
          newVal = newVal / listofNodes.length
          outcome = oldVal - newVal
          pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+7], valueIns: outcome})
          
          var transf9 = element.transf9
          corrMatrixCombLoc.push(Object.values(JSON.parse(transf9[5+quadrantNumberLocal])))
          corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf9[10+quadrantNumberLocal]))[0] * 100)
          VIFRemainingLoc.push(Object.values(JSON.parse(transf9[15+quadrantNumberLocal]))[0])
          MIRemainingLoc.push(JSON.parse(transf9[20+quadrantNumberLocal]))
          transf9 = JSON.parse(transf9[quadrantNumberLocal])
          oldVal = 0
          newVal = 0
          outcome = 0
          countLoc = 0
          Object.entries(transf9).forEach(
          function ([feature, value]) {
            var key = listofNodes[index]
            var search = Object.values(dataLoc[key])
            oldVal = Math.abs(search[countLoc]) + oldVal
            newVal = Math.abs(Object.values(value)[0]) + newVal
            countLoc++
          })
          oldVal = oldVal / listofNodes.length
          newVal = newVal / listofNodes.length
          outcome = oldVal - newVal
          pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+8], valueIns: outcome})

          var transf10 = element.transf10
          corrMatrixCombLoc.push(Object.values(JSON.parse(transf10[5+quadrantNumberLocal])))
          corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf10[10+quadrantNumberLocal]))[0] * 100)
          VIFRemainingLoc.push(Object.values(JSON.parse(transf10[15+quadrantNumberLocal]))[0])
          MIRemainingLoc.push(JSON.parse(transf10[20+quadrantNumberLocal]))
          transf10 = JSON.parse(transf10[quadrantNumberLocal])
          oldVal = 0
          newVal = 0
          outcome = 0
          countLoc = 0
          Object.entries(transf10).forEach(
          function ([feature, value]) {
            var key = listofNodes[index]
            var search = Object.values(dataLoc[key])
            oldVal = Math.abs(search[countLoc]) + oldVal
            newVal = Math.abs(Object.values(value)[0]) + newVal
            countLoc++
          })
          oldVal = oldVal / listofNodes.length
          newVal = newVal / listofNodes.length
          outcome = oldVal - newVal
          pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+9], valueIns: outcome})

          var transf11 = element.transf11
          corrMatrixCombLoc.push(Object.values(JSON.parse(transf11[5+quadrantNumberLocal])))
          corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf11[10+quadrantNumberLocal]))[0] * 100)
          VIFRemainingLoc.push(Object.values(JSON.parse(transf11[15+quadrantNumberLocal]))[0])
          MIRemainingLoc.push(JSON.parse(transf11[20+quadrantNumberLocal]))
          transf11 = JSON.parse(transf11[quadrantNumberLocal])
          oldVal = 0
          newVal = 0
          outcome = 0
          countLoc = 0
          Object.entries(transf11).forEach(
          function ([feature, value]) {
            var key = listofNodes[index]
            var search = Object.values(dataLoc[key])
            oldVal = Math.abs(search[countLoc]) + oldVal
            newVal = Math.abs(Object.values(value)[0]) + newVal
            countLoc++
          })
          oldVal = oldVal / listofNodes.length
          newVal = newVal / listofNodes.length
          outcome = oldVal - newVal
          pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+10], valueIns: outcome})

          var transf12 = element.transf12
          corrMatrixCombLoc.push(Object.values(JSON.parse(transf12[5+quadrantNumberLocal])))
          corrMatrixCombTotalLoc.push(Object.values(JSON.parse(transf12[10+quadrantNumberLocal]))[0] * 100)
          VIFRemainingLoc.push(Object.values(JSON.parse(transf12[15+quadrantNumberLocal]))[0])
          MIRemainingLoc.push(JSON.parse(transf12[20+quadrantNumberLocal]))
          transf12 = JSON.parse(transf12[quadrantNumberLocal])
          oldVal = 0
          newVal = 0
          outcome = 0
          countLoc = 0
          Object.entries(transf12).forEach(
          function ([feature, value]) {
            var key = listofNodes[index]
            var search = Object.values(dataLoc[key])
            oldVal = Math.abs(search[countLoc]) + oldVal
            newVal = Math.abs(Object.values(value)[0]) + newVal
            countLoc++
          })
          oldVal = oldVal / listofNodes.length
          newVal = newVal / listofNodes.length
          outcome = oldVal - newVal
          pushEach.push({keyIns: featureNames[(index)*numberOfTransformations+11], valueIns: outcome})
          pushEachFinal.push({key: listofNodes[index], value: pushEach})
        })

        this.corrMatrixComb = [...corrMatrixCombLoc]
        this.corrMatrixCombTotal = [...corrMatrixCombTotalLoc]
        this.VIFRemaining = [...VIFRemainingLoc]
        this.MIRemaining = [...MIRemainingLoc]

        var activeNodeLoc = this.activeLeafNode

        var nodes = []
        var groupID = 0
        listofNodes.forEach( function(element) {
          groupID++
          nodes.push({"name": element, "group": groupID+"_root"})
        })

        var links = []
        Object.entries(dataLoc).forEach(
            function ([feature, value]) {
              Object.entries(value).forEach( function ([featureInside, value]) {
                if (feature != featureInside) {
                  if (value >= threshLoc) {
                    links.push({"source": listofNodes.indexOf(feature), "target": listofNodes.indexOf(featureInside), "value": Math.abs(value) * 30, "lin_color": "#D3D3D3"})
                  } else {
                    links.push({"source": listofNodes.indexOf(feature), "target": listofNodes.indexOf(featureInside), "value": 0, "lin_color": "#D3D3D3"})
                  }
                }   
              })
        })

        if (activeNodeLoc != -1) {
          
          groupID = 0
          var featureNumber = 0
          listofNodes.forEach( function(element) {
            groupID++
            if ((activeNodeLoc+1) == groupID) {
              nodes.push(
                {"name": featureNames[(featureNumber)*numberOfTransformations+0], "group": groupID},
                {"name": featureNames[(featureNumber)*numberOfTransformations+1], "group": groupID},
                {"name": featureNames[(featureNumber)*numberOfTransformations+2], "group": groupID},
                {"name": featureNames[(featureNumber)*numberOfTransformations+3], "group": groupID},
                {"name": featureNames[(featureNumber)*numberOfTransformations+4], "group": groupID},
                {"name": featureNames[(featureNumber)*numberOfTransformations+5], "group": groupID},
                {"name": featureNames[(featureNumber)*numberOfTransformations+6], "group": groupID},
                {"name": featureNames[(featureNumber)*numberOfTransformations+7], "group": groupID},
                {"name": featureNames[(featureNumber)*numberOfTransformations+8], "group": groupID},
                {"name": featureNames[(featureNumber)*numberOfTransformations+9], "group": groupID},
                {"name": featureNames[(featureNumber)*numberOfTransformations+10], "group": groupID},
                {"name": featureNames[(featureNumber)*numberOfTransformations+11], "group": groupID},
              )
            }
            featureNumber++
          })

          Object.entries(pushEachFinal).forEach(
              function ([index, feature]) {
                if (index == activeNodeLoc) {
                  feature.value.forEach(function (element, indexIns) {
                    // if (element.valueIns > 0) {
                    //   links.push({"source": index, "target": (index*feature.value.length+pushEachFinal.length+indexIns), "value": Math.abs(element.valueIns) * 30, "lin_color": "#33a02c"})
                    // } else if (element.valueIns == 0) {
                    //   links.push({"source": index, "target": (index*feature.value.length+pushEachFinal.length+indexIns), "value": 0.01 * 30, "lin_color": "#D3D3D3"})
                    // } else {
                    //   links.push({"source": index, "target": (index*feature.value.length+pushEachFinal.length+indexIns), "value": Math.abs(element.valueIns) * 30, "lin_color": "#e31a1c"})
                    // }
                    if (element.valueIns > 0) {
                      if (Math.abs(element.valueIns) < 0.005) {
                        links.push({"source": index, "target": (pushEachFinal.length+indexIns), "value": 0.01 * 30, "lin_color": "#33a02c"})
                      } else {
                        links.push({"source": index, "target": (pushEachFinal.length+indexIns), "value": Math.abs(element.valueIns) * 30, "lin_color": "#33a02c"})
                      }
                    } else if (element.valueIns == 0) {
                      links.push({"source": index, "target": (pushEachFinal.length+indexIns), "value": 0.01 * 30, "lin_color": "#D3D3D3"})
                    } else {
                      if (Math.abs(element.valueIns) < 0.005) {
                        links.push({"source": index, "target": (pushEachFinal.length+indexIns), "value": 0.01 * 30, "lin_color": "#e31a1c"})
                      } else {
                        links.push({"source": index, "target": (pushEachFinal.length+indexIns), "value": Math.abs(element.valueIns) * 30, "lin_color": "#e31a1c"})
                      }
                    }
                  })
                }
          })        
        }

        this.jsonData = {"nodes": nodes, "links": links};
        this.graphVizualization()

      },
      graphVizualization () {
        var activeNodeLoc = this.activeLeafNode
        var svg = d3.select("#FeatureGraph");
        svg.selectAll("*").remove();
        var svg = d3.select('#chartID')
        svg.selectAll("*").remove()

        var legendCall = this.legendOnlyOnce

        var listofNodes = this.dataFS[34]
        var nodesStable = this.dataFS[33]

        var corrTarget = JSON.parse(this.dataFS[8+this.quadrantNumber])
        var corrGlob = JSON.parse(this.dataFS[13+this.quadrantNumber])
        var uniqueTarget = JSON.parse(this.dataFS[18+this.quadrantNumber])
        var VIFVar = JSON.parse(this.dataFS[23+this.quadrantNumber])
        var MIVar = JSON.parse(this.dataFS[28+this.quadrantNumber])
        MIVar = MIVar.concat(this.MIRemaining)
        //var colorCateg = d3.scaleOrdinal(d3.schemeDark2)
        var colorCateg = d3.scaleOrdinal().domain([0, 1, 2]).range(['#808000','#7570b3','#469990'])

        var corrTargetFormatted = []
        for (let i = 0; i < Object.keys(corrTarget).length; i++) {
          var corrTargetFormattedLoc = []
          for (let j = 0; j < Object.keys(corrTarget[i]).length; j++) {
            if (j > uniqueTarget.length - 1) {
              corrTargetFormattedLoc.push(Math.round(Object.values(corrTarget[i])[j] * 100))
            }
          }
          corrTargetFormatted.push(corrTargetFormattedLoc) 
        }

        for (let j = 0; j < uniqueTarget.length; j++) {
          for (let i = 0; i < Object.keys(this.corrMatrixComb).length; i++) {
            if (Math.round(Object.values((Object.values(this.corrMatrixComb[i])[j]))[0] * 100) == null) {
              corrTargetFormatted[j].push(0)
            } else {
              corrTargetFormatted[j].push(Math.round(Object.values((Object.values(this.corrMatrixComb[i])[j]))[0] * 100))
            }
          }
        }

        var corrGlobFormatted = []
        for (let i = 0; i < Object.keys(corrGlob).length; i++) {
          if (i != 0) {
            corrGlobFormatted.push(Math.round(Object.values(corrGlob)[i]['0'] * 100))
          }
        }

        for (let i = 0; i < this.corrMatrixCombTotal.length; i++) {
            corrGlobFormatted.push(Math.round(this.corrMatrixCombTotal[i]))
        }

        var VIFVarFormatted = []
        for (let i = 0; i < Object.keys(VIFVar).length; i++) {
          if (i != 0) {
            if (Object.values(VIFVar)[i] > 10) {
              VIFVarFormatted.push(100)
            } else if (Object.values(VIFVar)[i] > 5) {
              VIFVarFormatted.push(75)
            } else if (Object.values(VIFVar)[i] > 2.5) {
              VIFVarFormatted.push(50)
            } else {
              VIFVarFormatted.push(25)
            }
          }
        }

        for (let i = 0; i < this.VIFRemaining.length; i++) {
            if (Object.values(VIFVar)[i] > 10) {
              VIFVarFormatted.push(100)
            } else if (Object.values(VIFVar)[i] > 5) {
              VIFVarFormatted.push(75)
            } else if (Object.values(VIFVar)[i] > 2.5) {
              VIFVarFormatted.push(50)
            } else {
              VIFVarFormatted.push(25)
            }
          }

        function min(input) {
            if (toString.call(input) !== "[object Array]")  
              return false;
          return Math.min.apply(null, input);
        }

        function max(input) {
            if (toString.call(input) !== "[object Array]")  
              return false;
          return Math.max.apply(null, input);
        }

        function normalize(min, max) {
            var delta = max - min;
            return function (val) {
                return (val - min) / delta;
            };
        }

        var MIMin = min(MIVar)
        var MIMax = max(MIVar)

        MIVar = MIVar.map(normalize(MIMin, MIMax))
        var colorsScaleNodes = d3.scaleLinear()
          .domain(d3.ticks(0, 1, 5))
          .range(['#9ecae1','#6baed6','#4292c6','#2171b5','#08519c']);

        var marginNodes = {top: 0, right: 0, bottom: 0, left: 0};
        var width = 819 - marginNodes.right - marginNodes.left;
        var height = 819 - marginNodes.top - marginNodes.bottom;

        var numTicks = 200;

        var selectedParams;
        var bestParams;

        var dispatch = d3.dispatch('layoutend');

        svg = d3.select("#FeatureGraph").append("svg")
          .attr("width", width)
          .attr("height", height)
          .attr('transform', `translate(${marginNodes.left}, ${marginNodes.top})`);

        var graph = this.jsonData

        var link = svg.append('g')
          .attr('class', 'links')
          .selectAll('line')
          .data(graph.links)
          .enter().append('line')
          .attr("stroke", function(d) { return d.lin_color; })
          .attr("stroke-width", function(d) { return Math.sqrt(d.value); });
        
        var modeLoc = this.mode
        var selectionCounter = this.keepNumberOfCompareNodes
        var IDsGather = this.KeepIDs
        var IDsGatherTrans = this.KeepIDTransform
        var keepNames = this.KeepNamesGlobal

        var node = svg.append('g')
          .attr('class', 'nodes')
          .selectAll('g')
          .data(graph.nodes)
          .enter().append('g')
          .on("click", function(id, index) { 
            // This is for transformation
            if (modeLoc == 0) {
              var clickedNode = document.getElementById('svg'+index).getAttribute('class')
              if (!clickedNode.includes("root")) {
                var clearSendNode = []
                clearSendNode.push(id.name)
                var name = id.name
                var splitName = name.split("_")[0]
                for (let m = 0; m < nodesStable.length ; m++) {
                  var splitNodes = nodesStable[m].split("_")
                  if (splitNodes[0] === splitName) {
                    var valueToSend = m
                  }
                }
                
                clearSendNode.push(clickedNode-1)
                EventBus.$emit('updateHistoryKey', 2)
                EventBus.$emit('updateValuesofHistory', valueToSend)
                EventBus.$emit('UpdateIDTrans', [clickedNode-1])
                EventBus.$emit('transformNodes', clearSendNode)
              } else {
                // for (let i = 0; i < listofNodes.length; i++) {
                //   var numb = graph.nodes[i]['group'].match(/\d/g)
                //   numb = parseInt(numb.join(""))

                //   var items = document.getElementsByClassName(numb)

                //   items.forEach( function (it) {
                //     it.childNodes[0].style.visibility = "hidden";
                //     it.childNodes[1].setAttribute("transform", "translate(50,50) scale(0.32) rotate(180)");
                //     it.childNodes[1].childNodes[0].style.fill = "#D3D3D3";
                //     it.childNodes[2].style.visibility = "hidden";
                //   })
                // }

                // for (let i = 0; i < graph.nodes.length; i++) {
                //   var str = String(graph.nodes[i].group)
                //   // if (!str.includes("root")) {
                //   //   graph.nodes[i].active = false
                //   // } else {
                //   document.getElementsByClassName(str)[0].childNodes[0].childNodes[1].style.fill = "#D3D3D3"
                //   document.getElementById('svg'+index).childNodes[0].childNodes[1].style.fill = "#969696"
                //   //}
                // }

                // node.selectAll('text').remove();

                // var labels = node.append("text")
                //     .text(function(d) {
                //       return d.name;
                //     })
                //     .attr('x', function(d) {
                //       let characters = d.name.length
                //       return 41-Math.pow(characters,1.5)
                //     })
                //     .attr('y', function(d) {
                //       if(d.active)
                //         return 6
                //       else
                //         return 32
                //     });
              
                // node.append('title').text(function (d) { return d.name; });

                // var items = document.getElementsByClassName(groupLoc)
                // items.forEach( function (it) {
                //   if (it.childNodes[0].style.visibility == "hidden") {
                //     it.childNodes[0].style.visibility = "visible";
                //     it.childNodes[1].setAttribute("transform", "translate(50,50) scale(1) rotate(180)");
                //     it.childNodes[1].childNodes[0].style.fill = "none";
                //     it.childNodes[2].style.visibility = "visible";
                //   } else {
                //       it.childNodes[0].style.visibility = "hidden";
                //       it.childNodes[1].setAttribute("transform", "translate(50,50) scale(0.32) rotate(180)");
                //       it.childNodes[1].childNodes[0].style.fill = "#D3D3D3";
                //       it.childNodes[2].style.visibility = "hidden";
                //   }
                // })
                // var regex = /\d+/g
                // var string = id.group
                // var matches = parseInt(string.match(regex)[0])

                // for (let i = 0; i < graph.nodes.length; i++) {

                //   if (graph.nodes[i].group == matches) {
                //     graph.nodes[i].active = true
                //   }
                // }

                // node.selectAll('text').remove();

                // var labels = node.append("text")
                //     .text(function(d) {
                //       return d.name;
                //     })
                //     .attr('x', function(d) {
                //       let characters = d.name.length
                //       return 41-Math.pow(characters,1.5)
                //     })
                //     .attr('y', function(d) {
                //       if(d.active)
                //         return 6
                //       else
                //         return 32
                //     });
                var groupLoc = index + 1
                let length = document.getElementsByClassName(groupLoc).length
                // node.append('title').text(function (d) { return d.name; });
                if (length > 0) {
                  EventBus.$emit('UpdateIDTrans', [])
                  EventBus.$emit('brushLink', -1)
                } else {
                  EventBus.$emit('UpdateIDTrans', [groupLoc-1])
                  EventBus.$emit('brushLink', groupLoc-1)
                }
              }
            } else {
              var groupsColor = d3.select('#svg'+index)._groups['0'][0].childNodes[0].childNodes[1]
              var regex = /\d+/g
              var idLocal = parseInt(d3.select('#svg'+index)._groups['0'][0].getAttribute("id").match(regex))
              if (groupsColor.getAttribute('fill') == "#D3D3D3") {
                if (selectionCounter < 3) {
                  // add here the different states of comparison! (=2 and =3)
                  groupsColor.setAttribute('fill', '#969696')
                  selectionCounter = selectionCounter + 1
                  EventBus.$emit('Counter', selectionCounter)
                  var name = id.name
                  var splitName = name.split("_")[0]
                  for (let m = 0; m < nodesStable.length ; m++) {
                    var splitNodes = nodesStable[m].split("_")
                    if (splitNodes[0] === splitName) {
                      var valueToSend = m
                    }
                  }
                  console.log(valueToSend)
                  keepNames.push(valueToSend)
                  IDsGather.push(idLocal);
                  if (selectionCounter == 2) {
                    EventBus.$emit('updateValuesofHistory', keepNames)
                    EventBus.$emit('UpdateIDs', IDsGather)
                    EventBus.$emit('CompareTwo', IDsGather)
                  } else if (selectionCounter == 3) {
                    EventBus.$emit('updateValuesofHistory', keepNames)
                    EventBus.$emit('UpdateIDs', IDsGather)
                    EventBus.$emit('CompareThree', IDsGather)
                  } else {
                  }
                }
              } else {
                groupsColor.setAttribute('fill', '#D3D3D3')
                selectionCounter = selectionCounter - 1
                EventBus.$emit('Counter', selectionCounter)
                var index = IDsGather.indexOf(idLocal);
                if (index > -1) {
                  IDsGather.splice(index, 1);
                }
                EventBus.$emit('UpdateIDs', IDsGather)
                if (selectionCounter == 1) {
                  //EventBus.$emit('diactiveTransform')
                  //EventBus.$emit('Default')
                  EventBus.$emit('storeGeneration')
                } else if (selectionCounter == 2) {
                  EventBus.$emit('UpdateIDs', IDsGather)
                  EventBus.$emit('CompareTwo', IDsGather)
                } else {

                }
              }
            }
          });
          // .on("dblclick", function(id, index) {
          //   for (let i = 0; i < listofNodes.length; i++) {
          //     var numb = graph.nodes[i]['group'].match(/\d/g)
          //     numb = parseInt(numb.join(""))
          //     var items = document.getElementsByClassName(numb)
          //     items.forEach( function (it) {
          //       it.childNodes[0].style.visibility = "hidden";
          //       it.childNodes[1].setAttribute("transform", "translate(50,50) scale(0.32) rotate(180)");
          //       it.childNodes[1].childNodes[0].style.fill = "#D3D3D3";
          //       it.childNodes[2].style.visibility = "hidden";
          //     })
          //   }
          //   var regex = /\d+/g
          //   var string = id.group
          //   var matches = parseInt(string.match(regex)[0])

          //   for (let i = 0; i < graph.nodes.length; i++) {

          //     if (graph.nodes[i].group == matches) {
          //       graph.nodes[i].active = false
          //     } else {
          //       document.getElementById('svg'+index).childNodes[0].childNodes[1].style.fill = "#D3D3D3"
          //     }
          //   }

          //   node.selectAll('text').remove();

          //   var labels = node.append("text")
          //       .text(function(d) {
          //         return d.name;
          //       })
          //       .attr('x', function(d) {
          //         let characters = d.name.length
          //         return 41-Math.pow(characters,1.5)
          //       })
          //       .attr('y', function(d) {
          //         if(d.active)
          //           return 6
          //         else
          //           return 32
          //       });
          
          //   node.append('title').text(function (d) { return d.name; });
          //   EventBus.$emit('brushLink', -1)
          // });
        
        var chartWidth = 310;
        var chartHeight = 66;
        var margin = {left: 16, right: 15, top: 5, bottom: 45};
        var chartSvg = d3.select('svg.chart')
          .attr('width', chartWidth)
          .attr('height', chartHeight)
          .append('g')
          .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

        chartWidth = chartWidth - margin.left - margin.right;
        chartHeight = chartHeight - margin.top - margin.bottom;

        var x = d3.scaleLinear()
          .domain([0, 100])
          .range([0, chartWidth]);

        chartSvg.append('g')
            .attr('transform', 'translate(0,' + chartHeight + ')')
            .call(d3.axisBottom(x).ticks(7))
          .append("text")
            .attr("fill", "#000")
            .attr('transform', 'translate(' + chartWidth/2 + ',' + 0 + ')')
            .attr("y", chartHeight + 10)
            .attr("dy", "0.71em")
            .attr("text-anchor", "middle")
            .text("Weighted graph readability (%)");

        var readabilityCircles = chartSvg.append('g').selectAll('circle');

        // 48 parameter combinations
        var paramGroups = [ 
          {name: 'chargeStrength', values: [-80]},
          {name: 'linkDistance', values: [-80]},
          {name: 'linkStrength', values: [0.25, 0.5]},
          {name: 'gravity', values: [0, 0.5]},
          {name: 'iterations', values: [1, 2]},
          {name: 'alphaDecay', values: [0, 0.0228, 0.05]},
          {name: 'velocityDecay', values: [0.4, 0.8]}
        ];
        
        var paramList = generateParams(paramGroups);

        var bestSoFar = d3.select('.best').selectAll('li')
          .data(paramGroups.map(function (d) { return d.name; }))
          .enter().append('li')
          .text(function (d) { return d; });

        dispatch.on('layoutend', function (params, i) {

          if (!bestParams || params.graphReadability > bestParams.graphReadability) {
            bestParams = params;
            selectedParams = bestParams;

            bestSoFar
              .data(d3.map(bestParams).keys().filter(function (d) { return d !== 'positions' && d !== 'graphReadability'; }))
              .text(function (d) { return d + ' = ' + bestParams[d]; });
          }

            // Plot the number line.
            readabilityCircles = readabilityCircles
              .data(readabilityCircles.data().concat(params))
              .enter().append('circle')
              .attr('cx', function (d) { return x(d.graphReadability*100); })
              .attr('cy', 5)
              .attr('r', 4)
              .on('click', function (d) {
                selectedParams = d;
                readabilityCircles.classed('selected', false);
                d3.select(this).classed('selected', true).raise();

                bestSoFar
                  .data(d3.map(selectedParams).keys().filter(function (d) { return d !== 'positions' && d !== 'graphReadability'; }))
                  .text(function (d) { return d + ' = ' + selectedParams[d]; });

                drawGraph();
              })
              .merge(readabilityCircles)
              .classed('selected', function (d) { return d === selectedParams; });

            readabilityCircles.filter(function (d) { return d === selectedParams; })
              .raise();

            drawGraph();
        });

        var i = 0;
        var stepper = d3.timer(function () {
          var p = paramList[i];
          var forceSim = getForceSimFromParams(p);

          // Reset node attributes.
          graph.nodes.forEach(function (n) {
            n.x = n.y = n.vx = n.vy = 0;
          });

          forceSim.nodes(graph.nodes)
            .stop();

          forceSim.force('link')
            .links(graph.links);

          for (var t = 0; t < numTicks; ++t) {
            forceSim.tick();
          }

          p.graphReadability = greadability.greadability(graph.nodes, graph.links); // crossing > angularResolDev > angularResolMin > Angle
          p.graphReadability = (p.graphReadability.crossing * 1 + p.graphReadability.crossingAngle * 0.1 +
          p.graphReadability.angularResolutionMin * 0.4 + p.graphReadability.angularResolutionDev * 0.75) / 2.25

          p.positions = graph.nodes.map(function (n) { return {x: n.x, y: n.y}; });

          dispatch.call('layoutend', forceSim, p, i);

          ++i;
        
          if (i >= paramList.length) {

            var widthLoc = 100;
            var arcSize = (6 * widthLoc / 100);
            var arcSizeBlack = (10.2 * widthLoc / 100);
            var innerRadius = arcSize * 4.95; 
            var innerRadiusBlack = arcSize * 3.7

            var svgLoc = node.append('svg').attr('width', widthLoc).attr('height', widthLoc).attr("class", function(d, i) { return d.group; })
              .attr("id", function(d, i) { return "svg" + (i); })

            graph.nodes.forEach(function(itemVal, indexNode) {
              if (indexNode >= listofNodes.length) {
                var indexNodeTransf = activeNodeLoc*12+indexNode
              } else {
                var indexNodeTransf = indexNode
              }

              var data = []
              var barchartData = []
              
              if (IDsGather.includes(indexNode) || IDsGatherTrans.includes(indexNode)) {
                data.push({value: VIFVarFormatted[indexNodeTransf], color: '#969696'})
              } else {
                data.push({value: VIFVarFormatted[indexNodeTransf], color: '#D3D3D3'})
              }
              
              data.push({value: corrGlobFormatted[indexNodeTransf], color: colorsScaleNodes(MIVar[indexNodeTransf])})
              for(let k = 0; k < uniqueTarget.length; k++) {
                barchartData.push({value: corrTargetFormatted[k][indexNodeTransf], class: k, color: colorCateg(uniqueTarget[k])})
              }

              var length = data.length
              //data.push({value: 100, label: corrGlobFormatted[indexNode], color: 'black', lcolor: colorsScaleNodes(MIVar[indexNode])})

              //var border = VIFVarFormatted[indexNode]

                  var arcs = data.map(function (obj, i) {
                    if (i == length) {
                      return d3.arc().innerRadius(i * arcSize + innerRadius).outerRadius((i + 1) * arcSize - (widthLoc / 100) + innerRadius);
                    } else if (i == 0) {
                      return d3.arc().innerRadius(i * arcSizeBlack + innerRadiusBlack).outerRadius((i + 1) * arcSizeBlack - (widthLoc / 100) + innerRadiusBlack);
                    } else {
                      return d3.arc().innerRadius(i * arcSize + innerRadius).outerRadius((i + 1) * arcSize - (widthLoc / 100) + innerRadius);
                    }
                  });
                  
                  var arcsGrey = data.map(function (obj, i) {
                      return d3.arc().innerRadius(i * arcSize + (innerRadius + ((arcSize / 2) - 2))).outerRadius((i + 1) * arcSize - ((arcSize / 2)) + (innerRadius));
                  });

                  var pieData = data.map(function (obj, i) {
                      return [
                          {value: obj.value, arc: arcs[i], object: obj},
                          {value: (100 - obj.value), arc: arcsGrey[i], object: obj},
                          {value: 0, arc: arcs[i], object: obj}];
                  });

                  var pie = d3.pie().sort(null).value(function (d) {
                      return d.value;
                  });

                  var id = indexNode
                  var g = d3.select('#svg'+id).selectAll('g').data(pieData).enter()
                      .append('g')
                      .attr('transform', function(d, i) {
                        if (i == 0) {
                          return 'translate(' + widthLoc / 2 + ',' + widthLoc / 2 + ') rotate(225)'
                        } else {
                          return 'translate(' + widthLoc / 2 + ',' + widthLoc / 2 + ') rotate(180)'
                        } 
                      });

                  g.append("circle").attr("cx", 0).attr("cy", 0).attr("r", 38).attr("fill", function(d, i) {
                        if (i == 0) {  
                          return "white"
                        } else {
                          return "none"
                        }
                      });

                  var gText = d3.select('#svg'+id).selectAll('g.textClass').data([{}]).enter()
                      .append('g')
                      .classed('textClass', true)
                      .attr('transform', 'translate(' + 27.5 + ',' + 27.5 + ') rotate(0)');
                  var insideRadius = 0
                  g.selectAll('path').data(function (d) {
                      return pie(d);
                  }).enter().append('path')
                      .attr('id', function (d, i) {
                          if (i == 1) {
                              return "Text" + d.data.object.label
                          }
                      })
                      .attr('d', function (d) {
                          return d.data.arc(d);
                      }).attr('fill', function (d, i, j) {
                      if (i == 0) {
                        return d.data.object.color 
                      } else if (i == 1 && insideRadius != 0) {
                        return '#D3D3D3'
                      } else {
                        insideRadius = 1
                        return 'none'
                      }
                  })
                  var margin = {top: 0, right: 0, bottom: 0, left: 0},
                      width = 45 - margin.left - margin.right,
                      height = 45 - margin.top - margin.bottom;

                  g.each(function (d, index) {
                    var el = d3.select(this);
                    var path = el.selectAll('path').each(function (r, i) {
                      if (i === 1) {
                          
                        gText.append('svg')
                                .attr("width", width + margin.left + margin.right)
                                .attr("height", height + margin.top + margin.bottom)


                        gText.append("rect")
                            .attr("width", width)
                            .attr("height", height)
                            .attr("fill", "white");

                        // Add X axis
                          var x = d3.scaleLinear()
                            .domain([0, 100])
                            .range([ 0, width]);

                          // Y axis
                          var y = d3.scaleBand()
                            .range([ 0, height ])
                            .domain(barchartData.map(function(d) { return d.class; }))
                                .padding(.0);
                          //Bars
                          gText.selectAll("myRect")
                            .data(barchartData)
                            .enter()
                            .append("rect")
                            .attr("class", function(d){ return "bar"+d.class})
                            .attr("x", x(0) )
                            .attr("y", function(d) { return y(d.class); })
                            .attr("width", function(d) { return x(d.value); })
                            .attr("height", y.bandwidth() )
                            .attr("fill", function(d) { return d.color})
                            .attr('opacity', "0.5")
                            .on("mouseover", function(d) {
                              document.getElementsByClassName("bar"+d.class).forEach (function (element) {
                                element.setAttribute("opacity", "1.0")
                              })
                              document.getElementsByClassName("label"+d.class).forEach (function (element) {
                                element.setAttribute("visibility", "visible")
                              })
                            })
                            .on("mouseout", function(d, i) {
                              document.getElementsByClassName("bar"+d.class).forEach (function (element) {
                                element.setAttribute("opacity", "0.5")
                              })
                              document.getElementsByClassName("label"+d.class).forEach (function (element) {
                                element.setAttribute("visibility", "hidden")
                              })
                            });

                          gText.selectAll("myRect")
                            .data(barchartData)
                            .enter().append("text")
                          .attr("class", function(d){ return "label"+d.class})
                          //y position of the label is halfway down the bar
                          .attr("y", function (d) {
                              return y(d.class)+ 11;
                          })
                          //x position is 3 pixels to the right of the bar
                          .attr("x", function (d) {
                              return x(38);
                          })
                          .text(function (d) {
                              return d.value;
                          }).style("font-size", "10px")
                          .style("fill", function(d) {
                            return "black"
                          })
                          .attr("visibility", "hidden")
                      }
                      
                      // if (i == 0) {
                      //   // set the dimensions and margins of the graph
                      //   var margin = {top: 30, right: 30, bottom: 70, left: 60},
                      //       width = 460 - margin.left - margin.right,
                      //       height = 400 - margin.top - margin.bottom;

                      //   // append the svg object to the body of the page
                      //   var svg = d3.select("#my_dataviz")
                          
                      
                          // if (i === 1) {
                          //     var centroid = r.data.arc.centroid({
                          //         startAngle: r.startAngle + 0.05,
                          //         endAngle: r.startAngle + 0.001 + 0.05
                          //     });
                          //     var lableObj = r.data.object;
                          //     g.append('text')
                          //         .attr('font-size', ((2 * width) / 100))
                          //         .attr('dominant-baseline', 'central')
                          //         .append("textPath")
                          //         .attr("textLength", function (d, i) {
                          //             return 0;
                          //         })
                          //         .attr("startOffset", '5')
                          //         .attr("dy", '-3em')
                          //         .text(lableObj.value + '%');
                          // }
                          // if (i === 0) {
                          //     var centroidText = r.data.arc.centroid({
                          //         startAngle: r.startAngle,
                          //         endAngle: r.startAngle
                          //     });
                          //     var lableObj = r.data.object;
                          //     gText.append('text')
                          //         .attr('font-size', ((2 * width) / 100))
                          //         .text(lableObj.label)
                          //         .style('fill', lableObj.lcolor)
                          //         .attr('transform', "translate(" + (10) + "," + (0 + ") rotate(" + (180) + ")"))
                          //         .attr('dominant-baseline', 'central');
                          // }
                      });

                  });


                  // var drag_handler = d3.drag()
                  //   .on("start", drag_start)
                  //   .on("drag", drag_drag)
                  //   .on("end", drag_end);	
                    
                  // drag_handler(node);

                  
                })
                var labels = node.append("text")
                    .text(function(d) {
                      return d.name;
                    })
                    .attr('x', function(d) {
                      let characters = d.name.length
                      return 41-Math.pow(characters,1.5)
                    })
                    .attr('y', function(d) {
                      return 6
                    });
                  node.append('title').text(function (d, i) { 
                    if (i >= listofNodes.length) {
                      var indexNodeTransf = activeNodeLoc*12+i
                    } else {
                      var indexNodeTransf = i
                    }
                    return 'Target COR: '+String(corrGlobFormatted[indexNodeTransf])+'%';
                  });

                //add zoom capabilities 
                // var zoom_handler = d3.zoom()
                //     .on("zoom", zoom_actions);
                
                // zoom_handler(svg); 


                // for (let i = 0; i < listofNodes.length; i++) {
                //   var numb = graph.nodes[i]['group'].match(/\d/g)
                //   numb = parseInt(numb.join(""))
                //   var items = document.getElementsByClassName(numb)
                //   items.forEach( function (it) {
                //     it.childNodes[0].style.visibility = "hidden";
                //     it.childNodes[1].setAttribute("transform", "translate(50,50) scale(0.32) rotate(180)");
                //     it.childNodes[1].childNodes[0].style.fill = "#D3D3D3";
                //     it.childNodes[2].style.visibility = "hidden";
                //   })
                // }

                //Zoom functions 
                // function zoom_actions(){
                //   svg.attr("transform", d3.event.transform)
                // }

                // function drag_start(d) {
                //   if (!d3.event.active) forceSim.alphaTarget(0.3).restart();
                //       d.fx = d.x;
                //       d.fy = d.y;
                //   }

                //   //make sure you can't drag the circle outside the box
                //   function drag_drag(d) {
                //     d.fx = d3.event.x;
                //     d.fy = d3.event.y;
                //     tickActions();
                //   }

                //   function drag_end(d) {
                //     if (!d3.event.active) forceSim.alphaTarget(0);
                //     d.fx = null;
                //     d.fy = null;
                //   }

                if (legendCall) {

                  var svgLegend = d3.select("#legend").append("svg")
                    .attr("width", 170)
                    .attr("height", 90)
                    .attr("id", "legendNode")

                  var dataLegend = []
                  var binaryBarLegend = []
                  var exemplaryValues = [25, 75]

                  dataLegend.push({value: 25, color: '#D3D3D3'})
                  dataLegend.push({value: 50, color: '#4292c6'})

                  for(let k = 0; k < 2; k++) {
                    binaryBarLegend.push({value: exemplaryValues[k], class: k, color: colorCateg(k)})
                  }

                  var lengthLeg = dataLegend.length

                  var arcsLegend = dataLegend.map(function (obj, i) {
                      if (i == lengthLeg) {
                        return d3.arc().innerRadius(i * arcSize + innerRadius).outerRadius((i + 1) * arcSize - (widthLoc / 100) + innerRadius);
                      } else if (i == 0) {
                        return d3.arc().innerRadius(i * arcSizeBlack + innerRadiusBlack).outerRadius((i + 1) * arcSizeBlack - (widthLoc / 100) + innerRadiusBlack);
                      } else {
                        return d3.arc().innerRadius(i * arcSize + innerRadius).outerRadius((i + 1) * arcSize - (widthLoc / 100) + innerRadius);
                      }
                    });
                    
                    var arcsGreyLegend = dataLegend.map(function (obj, i) {
                        return d3.arc().innerRadius(i * arcSize + (innerRadius + ((arcSize / 2) - 2))).outerRadius((i + 1) * arcSize - ((arcSize / 2)) + (innerRadius));
                    });

                    var pieDataLegend = dataLegend.map(function (obj, i) {
                        return [
                            {value: obj.value, arc: arcsLegend[i], object: obj},
                            {value: (100 - obj.value), arc: arcsGreyLegend[i], object: obj},
                            {value: 0, arc: arcsLegend[i], object: obj}];
                    });

                    var pieLegend = d3.pie().sort(null).value(function (d) {
                        return d.value;
                    });

                    var gLegend = d3.select('#legendNode').selectAll('g').data(pieDataLegend).enter()
                        .append('g')
                        .attr('transform', function(d, i) {
                          if (i == 0) {
                            return 'translate(' + widthLoc / 2 + ',' + widthLoc / 2 + ') rotate(225)'
                          } else {
                            return 'translate(' + widthLoc / 2 + ',' + widthLoc / 2 + ') rotate(180)'
                          } 
                        });

                    gLegend.append("circle").attr("cx", 0).attr("cy", 0).attr("r", 38).attr("fill", function(d, i) {
                          if (i == 0) {  
                            return "white"
                          } else {
                            return "none"
                          }
                        });

                    var gTextLegend = d3.select('#legendNode').selectAll('g.textClass').data([{}]).enter()
                        .append('g')
                        .classed('textClass', true)
                        .attr('transform', 'translate(' + 27.5 + ',' + 27.5 + ') rotate(0)');
                    var insideRadius = 0
                    gLegend.selectAll('path').data(function (d) {
                        return pieLegend(d);
                    }).enter().append('path')
                        .attr('id', function (d, i) {
                            if (i == 1) {
                                return "Text" + d.data.object.label
                            }
                        })
                        .attr('d', function (d) {
                            return d.data.arc(d);
                        }).attr('fill', function (d, i, j) {
                        if (i == 0) {
                          return d.data.object.color 
                        } else if (i == 1 && insideRadius != 0) {
                          return '#D3D3D3'
                        } else {
                          insideRadius = 1
                          return 'none'
                        }
                    });

                    var margin = {top: 0, right: 0, bottom: 0, left: 0},
                        width = 45 - margin.left - margin.right,
                        height = 45 - margin.top - margin.bottom;
                    gLegend.each(function (d, index) {
                      var el = d3.select(this);
                      var path = el.selectAll('path').each(function (r, i) {
                        if (i === 1) {

                          gTextLegend.append('svg')
                                  .attr("width", width + margin.left + margin.right)
                                  .attr("height", height + margin.top + margin.bottom)


                          gTextLegend.append("rect")
                              .attr("width", width)
                              .attr("height", height)
                              .attr("fill", "white");

                          // Add X axis
                            var x = d3.scaleLinear()
                              .domain([0, 100])
                              .range([ 0, width]);

                            // Y axis
                            var y = d3.scaleBand()
                              .range([ 0, height ])
                              .domain(binaryBarLegend.map(function(d) { return d.class; }))
                                  .padding(.0);
                            //Bars
                            gTextLegend.selectAll("myRect")
                              .data(binaryBarLegend)
                              .enter()
                              .append("rect")
                              .attr("x", x(0) )
                              .attr("y", function(d) { return y(d.class); })
                              .attr("width", function(d) { return x(d.value); })
                              .attr("height", y.bandwidth() )
                              .attr("fill", function(d) { return d.color})
                              .attr("opacity", "0.5")
                        }
                    })
                  });

                  var textLine = d3.select('#legendText').append("svg").attr('width', 170).attr('height', 90)

                  var marginBorder = 16
                  var marginBorderX = 5

                  const markerBoxWidth = 2;
                  const markerBoxHeight = 2;
                  const refX = markerBoxWidth / 2;
                  const refY = markerBoxHeight / 2;
                  const arrowPoints = [[0, 0], [0, 2], [2, 1]];

                  textLine.append("svg:defs").append("svg:marker")
                      .attr("id", "triangle")
                      .attr("refX", refX)
                      .attr("refY", refY)
                      .attr("markerWidth", markerBoxWidth)
                      .attr("markerHeight", markerBoxHeight)
                      .attr("orient", "auto")
                      .append("path")
                      .attr('d', d3.line()(arrowPoints))
                      .style("fill", "black");

                  textLine.append("svg:defs").append("svg:marker")
                      .attr("id", "triangle2")
                      .attr("refX", refX)
                      .attr("refY", refY)
                      .attr("markerWidth", markerBoxWidth)
                      .attr("markerHeight", markerBoxHeight)
                      .attr("orient", "auto")
                      .append("path")
                      .attr('d', d3.line()(arrowPoints))
                      .style("fill", "black");

                    
                  textLine.append("svg:defs").append("svg:marker")
                      .attr("id", "triangle3")
                      .attr("refX", refX)
                      .attr("refY", refY)
                      .attr("markerWidth", markerBoxWidth)
                      .attr("markerHeight", markerBoxHeight)
                      .attr("orient", "auto")
                      .append("path")
                      .attr('d', d3.line()(arrowPoints))
                      .style("fill", "black");


                  textLine.append("svg:defs").append("svg:marker")
                       .attr("id", "triangle4")
                      .attr("refX", refX)
                      .attr("refY", refY)
                      .attr("markerWidth", markerBoxWidth)
                      .attr("markerHeight", markerBoxHeight)
                      .attr("orient", "auto-start-reverse")
                      .append("path")
                      .attr('d', d3.line()(arrowPoints))
                      .style("fill", "#4292c6");


                  //line              
                  textLine.append("line")
                    .style("stroke", "black")
                    .style("stroke-width", 3)
                    .attr("x1", 36 + marginBorderX)
                    .attr("y1", 50 - marginBorder)
                    .attr("x2", 74 + marginBorderX)
                    .attr("y2", 50 - marginBorder)
                    .attr("marker-end", "url(#triangle)");

                  textLine.append("text")
                    .attr("dx", 77 + marginBorderX)
                    .attr("dy", 55 - marginBorder)
                    .text("VIF")

                  textLine.append('line')
                    .style("stroke", "black")
                    .style("stroke-width", 3)
                    .attr("x1", 44 + marginBorderX)
                    .attr("y1", 31 - marginBorder)
                    .attr("x2", 53 + marginBorderX)
                    .attr("y2", 31 - marginBorder)
                    .attr("marker-end", "url(#triangle2)");
                  
                  textLine.append("text")
                    .attr("dx", 56 + marginBorderX)
                    .attr("dy", 36 - marginBorder)
                    .text("Per class COR")

                  textLine.append('line')
                    .style("stroke", "black")
                    .style("stroke-width", 3)
                    .attr("x1", 32 + marginBorderX) 
                    .attr("y1", 67 - marginBorder)
                    .attr("x2", 74 + marginBorderX)
                    .attr("y2", 67 - marginBorder)
                    .attr("marker-end", "url(#triangle3)");
                  
                  textLine.append("text")
                    .attr("dx", 77 + marginBorderX)
                    .attr("dy", 72 - marginBorder)
                    .text("Target COR")

                  textLine.append('line')
                    .style("stroke", "#4292c6")
                    .style("stroke-width", 3)
                    .attr("x1", 18 + marginBorderX)
                    .attr("y1", 50 - marginBorder)
                    .attr("x2", 26 + marginBorderX)
                    .attr("y2", 50 - marginBorder)
                    .attr("marker-start", "url(#triangle4)");
                  
                  textLine.append("text")
                    .attr("dx", -2 + marginBorderX)
                    .attr("dy", 55 - marginBorder)
                    .style("fill", "#4292c6")
                    .text("MI")
            }
            stepper.stop();
            // if (IDsGatherTrans != '') {
            //   let ID = document.getElementsByClassName(IDsGatherTrans)[0].parentElement.getAttribute('id')
            //   d3.select('#'+ID).dispatch('click');
            //   IDsGatherTrans = ''
            // }
          }

        });

        function tickActions() {
          link
            .attr('x1', function (d) { return d.source.x; })
            .attr('x2', function (d) { return d.target.x; })
            .attr('y1', function (d) { return d.source.y; })
            .attr('y2', function (d) { return d.target.y; });

          node
            .attr("id", function(d, i) { return "g" + (i); })
            .attr("transform", function(d, i) {
              d.x = d.x - 52
              d.y = d.y - 45
              return "translate(" + d.x + "," + d.y + ")";
            })
        };

        function drawGraph () {
          graph.nodes.forEach(function (n, i) {
            n.x = selectedParams.positions[i].x;
            n.y = selectedParams.positions[i].y;
          });

          var xDistance = d3.extent(graph.nodes, function (n) { return n.x; });
          var xMin = xDistance[0];
          xDistance = xDistance[1] - xDistance[0];

          var yDistance = d3.extent(graph.nodes, function (n) { return n.y; });
          var yMin = yDistance[0];
          yDistance = yDistance[1] - yDistance[0];

          graph.nodes.forEach(function (n, i) {
            n.x = (height - 105) * (n.x - xMin) / Math.max(xDistance, yDistance); // Margin for Nodes
            n.y = (height - 105) * (n.y - yMin) / Math.max(xDistance, yDistance); // Margin for Nodes
          });

          xDistance = d3.extent(graph.nodes, function (n) { return n.x; });
          var xMid = (xDistance[1] + xDistance[0]) / 2;
          yDistance = d3.extent(graph.nodes, function (n) { return n.y; });
          var yMid = (yDistance[1] - yDistance[0]) / 2;

          graph.nodes.forEach(function (n, i) {
            n.x = n.x + width/2 - xMid;
            n.y = n.y + height/2 - yMid;
          });

          tickActions();
        }

        function generateParams (paramGroups, paramList, currParam) {
          var p = paramGroups[0];

          if (!paramList) paramList = [];

          if (!currParam) currParam = {};

          p.values.forEach(function (v) {
            var setting = {};
            setting[p.name] = v;
            if (paramGroups.length === 1) {
              paramList.push(Object.assign(setting, currParam));
            } else {
              generateParams(paramGroups.slice(1), paramList, Object.assign(setting, currParam));
            }
          });

          return paramList;
        }

        function getForceSimFromParams (params) {
          var forceSim = d3.forceSimulation()
            .force('link', d3.forceLink().iterations(params.iterations))
            .force('charge', d3.forceManyBody().strength(params.chargeStrength))
            .force('x', d3.forceX(0).strength(params.gravity))
            .force('y', d3.forceY(0).strength(params.gravity))
            .force('center', d3.forceCenter(0, 0))
            .alphaDecay(params.alphaDecay)
            .velocityDecay(params.velocityDecay);

          if (params.linkStrength !== null) {
            forceSim.force('link').strength(params.linkStrength);
          }

          return forceSim;
        }

        this.legendOnlyOnce = false
      },
      reset () {
        var svg = d3.select("#FeatureGraph");
        svg.selectAll("*").remove();
        var svg = d3.select('#chartID')
        svg.selectAll("*").remove()
      },
    },
  mounted () {
    EventBus.$on('brushLink', data => { this.activeLeafNode = data })
    EventBus.$on('brushLink', this.initializeNetwork)

    EventBus.$on('Counter', data => { this.keepNumberOfCompareNodes = data })
    EventBus.$on('UpdateIDs', data => { this.KeepIDs = data })
    EventBus.$on('UpdateNames', data => { this.KeepNamesGlobal = data })

    EventBus.$on('UpdateIDTrans', data => { this.KeepIDTransform = data })

    this.InitSlider()
    EventBus.$on('CorrThres', data => { this.threshold = data })
    EventBus.$on('CorrThres', this.initializeNetwork)

    EventBus.$on('updateSlice', data => { this.quadrantNumber = data })
    EventBus.$on('updateSlice', this.initializeNetwork)
    //EventBus.$on('updateSlice', this.setLayerExplore)
    //EventBus.$on('updateSlice', this.initializeNetwork)

    EventBus.$on('quadTrans', data => { this.dataFSTrans = data })
    EventBus.$on('quad', data => { this.dataFS = data })
    EventBus.$on('quad', this.computeOnce)
    EventBus.$on('quad', this.initializeNetwork)

    EventBus.$on('removeFeatures', data => { this.featureAddRemCount = data })

    EventBus.$on('reset', this.reset)

    EventBus.$on('flagSpace', data => { this.spaceChangeDetail = data })

    // Get the container element
    var btnContainer2 = document.getElementById("resetAllFilters"); //resetAllFilters button
    // Get all buttons with class="btn" inside the container
    var btns2 = btnContainer2.getElementsByClassName("btn");

    for (var i = 0; i < btns2.length; i++) {
      btns2[i].addEventListener("click", function() {
      let current = document.getElementsByClassName("active");
      current[0].className = current[0].className.replace("btn btn-primary active", "btn btn-primary");
      this.className += " active";
      });
    }
  }
}
</script>

<style>

#buildLegend { position: relative}
#legend { position: absolute; top: 0; left: 0; z-index: 1}
#legendText { position: absolute; top: 0; left: 0; z-index: 2}

#floatingPanel { 
  position: absolute;
  transform: translate(-1068px, -33px);
}

#glyphLegend {
  position: absolute;
  transform: translate(210px, 6px) !important;
}

#legend { 
  transform: translateY(-47px) scale(0.8) !important
}

#legendText { 
  transform: translateY(-47px) !important
}

text {
  font-family: sans-serif;
  font-size: 16px
}

svg {
  display: block;
}

.links line {
  stroke-opacity: 0.6;
}

.column {
  float: left;
}

.table {
  padding: 0 !important;
  margin: 0 !important;
}

table td {
  vertical-align: middle !important;
  padding: 2 !important;
  margin: 0 !important;
}

.centerTable {
  text-align: center; 
}

/* Dropdown Button */
.dropbtn {
  background-color: rgb(185, 185, 185);
  color: black;
  padding: 14px;
  border: none;
  cursor: pointer;
  }

.col, .col-1, .col-10, .col-11, .col-12, .col-2, .col-3, .col-4, .col-5, .col-6, .col-7, .col-8, .col-9, .col-auto, .col-lg, .col-lg-1, .col-lg-10, .col-lg-11, .col-lg-12, .col-lg-2, .col-lg-3, .col-lg-4, .col-lg-5, .col-lg-6, .col-lg-7, .col-lg-8, .col-lg-9, .col-lg-auto, .col-md, .col-md-1, .col-md-10, .col-md-11, .col-md-12, .col-md-2, .col-md-3, .col-md-4, .col-md-5, .col-md-6, .col-md-7, .col-md-8, .col-md-9, .col-md-auto, .col-sm, .col-sm-1, .col-sm-10, .col-sm-11, .col-sm-12, .col-sm-2, .col-sm-3, .col-sm-4, .col-sm-5, .col-sm-6, .col-sm-7, .col-sm-8, .col-sm-9, .col-sm-auto, .col-xl, .col-xl-1, .col-xl-10, .col-xl-11, .col-xl-12, .col-xl-2, .col-xl-3, .col-xl-4, .col-xl-5, .col-xl-6, .col-xl-7, .col-xl-8, .col-xl-9, .col-xl-auto {
  padding-right: 6px !important;
  padding-left: 6px !important;
}

#chartID {
  position: absolute;
  transform: translate(-351px, 845px);
  border: 1px solid black !important;
}

.chart circle {
  fill: black;
  fill-opacity: 0.05;
  stroke: black;
  stroke-opacity: 0.05;
  cursor: pointer;
}

.chart circle.selected {
  fill: #0062cc;
  fill-opacity: 1;
  stroke: #0062cc;
  stroke-opacity: 1;
}

</style>