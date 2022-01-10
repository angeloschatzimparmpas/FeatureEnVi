<template>
<div>
  <div id="tree-container" style="min-height: 820px"></div>
  <div id="toolbar">
    <div class="tool">
      <div class="tlabel">Zoom</div>
      <div class="tbuttons">
        <div class="button" data-key="187" title="Zoom In">+</div>
        <div class="button" data-key="189" title="Zoom Out">&minus;</div>
      </div>
    </div>
    <div class="tool">
      <div class="tlabel">Rotate</div>
      <div class="tbuttons">
        <div class="button" data-key="33" title="Rotate CCW" style="font-size:0.9em">&#8634;</div>
        <div class="button" data-key="34" title="Rotate CW" style="font-size:0.9em">&#8635;</div>
      </div>
    </div>
    <!--<div class="tool">
      <div class="tlabel">Select</div>
      <div class="tbuttons">
        <div class="button" data-key="-38" title="Select Previous" style="font-size:0.9em">&#8613;</div>
        <div class="button" data-key="-40" title="Select Next" style="font-size:0.9em">&#8615;</div>
      </div>
    </div>-->
    <div class="tool">
      <div class="tlabel">View</div>
      <div class="tbuttons">
        <div class="button" data-key="36" title="Center Root">&#8962;</div>
        <div class="button" data-key="35" title="Center Selected" style="font-size:0.8em">&#9673;</div>
      </div>
    </div>
    <div class="tool">
      <div class="tlabel">Toggle</div>
      <div class="tbuttons">
        <div class="button" data-key="32" title="Toggle Node">1</div>
        <div class="button" data-key="13" title="Toggle Level">&oplus;</div>
        <div class="button" data-key="191" title="Toggle Root">/</div>
      </div>
    </div>
    <div class="tool" id="moveNavigate">
      <div class="tlabel" style="text-align:left" title="Change Root">&nbsp;Navigate</div>
      <div id="selection" class="tlabel"></div>
    </div>
    <div class="tool" id="moveLabel">
      <div id="help">Labels</div>
      <div id="legendTarget" style="min-width: 132px; min-height: 50px; margin-top:-10px"></div>
    </div>
  </div>

  <div id="contextmenu">
    <div data-key="32"><span class="expcol">Expand</span> Node</div>
    <div data-key="13">Expand 1 Level</div>
    <div data-key="-13">Expand Full Tree</div>
    <div data-key="35">Center This Node</div>
    <div data-key="36">Center Root</div>
    <div data-key="191">Set Root</div>
  </div>
</div>
</template>

<script>
import { EventBus } from '../main.js'
import * as greadability from '../greadability.js'
import * as Plotly from 'plotly.js'
import * as d3Base from 'd3'
import $ from 'jquery'

// attach all d3 plugins to the d3 library
const d3v5 = Object.assign(d3Base)

export default {
  name: 'FeatureSpaceOverview',
  data () {
    return {
      colorsReceive: [],
      activeLeaf: -1,
      overallData: [],
      overallDataTransfCorr: [],
      overallDataTransfMI: [],
      keepRoot: 1,
      collapsed: []
    }
  },
  methods: {
      reset () {
        var svg = d3.select("#tree-container");
        svg.selectAll("*").remove();
        var svg = d3.select("#legendTarget")
        svg.selectAll("*").remove();
      },
      // Get JSON data
      initializeRadialTree() {
        var svg = d3.select("#legendTarget")
        svg.selectAll("*").remove();
        var svg = d3.select("#tree-container");
        svg.selectAll("*").remove();   

        var features = this.colorsReceive
        var activeLeafLoc = this.activeLeaf
        var listofNodes = this.overallData[34]

        var corrGlob1 = JSON.parse(this.overallData[13])
        var corrGlob2 = JSON.parse(this.overallData[14])
        var corrGlob3 = JSON.parse(this.overallData[15])
        var corrGlob4 = JSON.parse(this.overallData[16])
        var corrGlob5 = JSON.parse(this.overallData[17])

        var MIVar1 = []
        var MIVar2 = []
        var MIVar3 = []
        var MIVar4 = []
        var MIVar5 = []

        var MIVar1 = JSON.parse(this.overallData[28])
        var MIVar2 = JSON.parse(this.overallData[29])
        var MIVar3 = JSON.parse(this.overallData[30])
        var MIVar4 = JSON.parse(this.overallData[31])
        var MIVar5 = JSON.parse(this.overallData[32])

        MIVar1 = MIVar1.concat(this.overallDataTransfMI[0])
        MIVar2 = MIVar2.concat(this.overallDataTransfMI[1])
        MIVar3 = MIVar3.concat(this.overallDataTransfMI[2])
        MIVar4 = MIVar4.concat(this.overallDataTransfMI[3])
        MIVar5 = MIVar5.concat(this.overallDataTransfMI[4])
        
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

        var MIMin1 = min(MIVar1)
        var MIMax1 = max(MIVar1)
        var MIMin2 = min(MIVar2)
        var MIMax2 = max(MIVar2)
        var MIMin3 = min(MIVar3)
        var MIMax3 = max(MIVar3)
        var MIMin4 = min(MIVar4)
        var MIMax4 = max(MIVar4)
        var MIMin5 = min(MIVar5)
        var MIMax5 = max(MIVar5)

        var storeRootIndices = []
        var firstTime = true

        MIVar1 = MIVar1.map(normalize(MIMin1, MIMax1))
        MIVar2 = MIVar2.map(normalize(MIMin2, MIMax2))
        MIVar3 = MIVar3.map(normalize(MIMin3, MIMax3))
        MIVar4 = MIVar4.map(normalize(MIMin4, MIMax4))
        MIVar5 = MIVar5.map(normalize(MIMin5, MIMax5))

        var colorsScaleNodes = d3v5.scaleLinear()
          .domain(d3v5.ticks(0, 1, 5))
          .range(['#9ecae1','#6baed6','#4292c6','#2171b5','#08519c']);

        var featuresQuad1 = []
        var featuresQuad2 = []
        var featuresQuad3 = []
        var featuresQuad4 = []
        var featuresQuad5 = []
          // 4 is number of transformations!
        for (let i = 0; i < features[4].length; i++) {
          featuresQuad1.push({"name": features[0][i].key,
            "children": [  
              {"name": features[0][i].value[0].keyIns, "lin_color": features[0][i].value[0].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[0][i*12+0]), "MI_pick":colorsScaleNodes(MIVar1[features[4].length+i*12+0])},
              {"name": features[0][i].value[1].keyIns, "lin_color": features[0][i].value[1].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[0][i*12+1]), "MI_pick":colorsScaleNodes(MIVar1[features[4].length+i*12+1])},
              {"name": features[0][i].value[2].keyIns, "lin_color": features[0][i].value[2].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[0][i*12+2]), "MI_pick":colorsScaleNodes(MIVar1[features[4].length+i*12+2])},
              {"name": features[0][i].value[3].keyIns, "lin_color": features[0][i].value[3].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[0][i*12+3]), "MI_pick":colorsScaleNodes(MIVar1[features[4].length+i*12+3])},
              {"name": features[0][i].value[4].keyIns, "lin_color": features[0][i].value[4].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[0][i*12+4]), "MI_pick":colorsScaleNodes(MIVar1[features[4].length+i*12+4])},
              {"name": features[0][i].value[5].keyIns, "lin_color": features[0][i].value[5].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[0][i*12+5]), "MI_pick":colorsScaleNodes(MIVar1[features[4].length+i*12+5])},
              {"name": features[0][i].value[6].keyIns, "lin_color": features[0][i].value[6].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[0][i*12+6]), "MI_pick":colorsScaleNodes(MIVar1[features[4].length+i*12+6])},
              {"name": features[0][i].value[7].keyIns, "lin_color": features[0][i].value[7].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[0][i*12+7]), "MI_pick":colorsScaleNodes(MIVar1[features[4].length+i*12+7])},
              {"name": features[0][i].value[8].keyIns, "lin_color": features[0][i].value[8].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[0][i*12+8]), "MI_pick":colorsScaleNodes(MIVar1[features[4].length+i*12+8])},
              {"name": features[0][i].value[9].keyIns, "lin_color": features[0][i].value[9].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[0][i*12+9]), "MI_pick":colorsScaleNodes(MIVar1[features[4].length+i*12+9])},
              {"name": features[0][i].value[10].keyIns, "lin_color": features[0][i].value[10].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[0][i*12+10]), "MI_pick":colorsScaleNodes(MIVar1[features[4].length+i*12+10])},
              {"name": features[0][i].value[11].keyIns, "lin_color": features[0][i].value[11].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[0][i*12+11]), "MI_pick":colorsScaleNodes(MIVar1[features[4].length+i*12+11])},
            ],
            "lin_color": features[0][i].value[0].valueIns+features[0][i].value[1].valueIns+features[0][i].value[2].valueIns+features[0][i].value[3].valueIns+features[0][i].value[4].valueIns+features[0][i].value[5].valueIns+features[0][i].value[6].valueIns+features[0][i].value[7].valueIns+features[0][i].value[8].valueIns+features[0][i].value[9].valueIns+features[0][i].value[10].valueIns+features[0][i].value[11].valueIns,
            "Corr_pick": Math.round(Object.values(corrGlob1)[i+1]['0'] * 100),
            "MI_pick": colorsScaleNodes(MIVar1[i])
            })
          featuresQuad2.push({"name": features[1][i].key,
            "children": [  
              {"name": features[1][i].value[0].keyIns, "lin_color": features[1][i].value[0].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[1][i*12+0]), "MI_pick":colorsScaleNodes(MIVar2[features[4].length+features[4].length+i*12+0])},
              {"name": features[1][i].value[1].keyIns, "lin_color": features[1][i].value[1].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[1][i*12+1]), "MI_pick":colorsScaleNodes(MIVar2[features[4].length+features[4].length+i*12+1])},
              {"name": features[1][i].value[2].keyIns, "lin_color": features[1][i].value[2].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[1][i*12+2]), "MI_pick":colorsScaleNodes(MIVar2[features[4].length+features[4].length+i*12+2])},
              {"name": features[1][i].value[3].keyIns, "lin_color": features[1][i].value[3].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[1][i*12+3]), "MI_pick":colorsScaleNodes(MIVar2[features[4].length+i*12+3])},
              {"name": features[1][i].value[4].keyIns, "lin_color": features[1][i].value[4].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[1][i*12+4]), "MI_pick":colorsScaleNodes(MIVar2[features[4].length+i*12+4])},
              {"name": features[1][i].value[5].keyIns, "lin_color": features[1][i].value[5].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[1][i*12+5]), "MI_pick":colorsScaleNodes(MIVar2[features[4].length+i*12+5])},
              {"name": features[1][i].value[6].keyIns, "lin_color": features[1][i].value[6].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[1][i*12+6]), "MI_pick":colorsScaleNodes(MIVar2[features[4].length+i*12+6])},
              {"name": features[1][i].value[7].keyIns, "lin_color": features[1][i].value[7].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[1][i*12+7]), "MI_pick":colorsScaleNodes(MIVar2[features[4].length+i*12+7])},
              {"name": features[1][i].value[8].keyIns, "lin_color": features[1][i].value[8].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[1][i*12+8]), "MI_pick":colorsScaleNodes(MIVar2[features[4].length+i*12+8])},
              {"name": features[1][i].value[9].keyIns, "lin_color": features[1][i].value[9].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[1][i*12+9]), "MI_pick":colorsScaleNodes(MIVar2[features[4].length+i*12+9])},
              {"name": features[1][i].value[10].keyIns, "lin_color": features[1][i].value[10].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[1][i*12+10]), "MI_pick":colorsScaleNodes(MIVar2[features[4].length+i*12+10])},
              {"name": features[1][i].value[11].keyIns, "lin_color": features[1][i].value[11].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[1][i*12+11]), "MI_pick":colorsScaleNodes(MIVar2[features[4].length+i*12+11])},
            ],
            "lin_color": features[1][i].value[0].valueIns+features[1][i].value[1].valueIns+features[1][i].value[2].valueIns+features[1][i].value[3].valueIns+features[1][i].value[4].valueIns+features[1][i].value[5].valueIns+features[1][i].value[6].valueIns+features[1][i].value[7].valueIns+features[1][i].value[8].valueIns+features[1][i].value[9].valueIns+features[1][i].value[10].valueIns+features[1][i].value[11].valueIns,
            "Corr_pick": Math.round(Object.values(corrGlob2)[i+1]['0'] * 100),
            "MI_pick": colorsScaleNodes(MIVar2[i])
            })
          featuresQuad3.push({"name": features[2][i].key,
            "children": [  
              {"name": features[2][i].value[0].keyIns, "lin_color": features[2][i].value[0].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[2][i*12+0]), "MI_pick":colorsScaleNodes(MIVar3[features[4].length+i*12+0])},
              {"name": features[2][i].value[1].keyIns, "lin_color": features[2][i].value[1].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[2][i*12+1]), "MI_pick":colorsScaleNodes(MIVar3[features[4].length+i*12+1])},
              {"name": features[2][i].value[2].keyIns, "lin_color": features[2][i].value[2].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[2][i*12+2]), "MI_pick":colorsScaleNodes(MIVar3[features[4].length+i*12+2])},
              {"name": features[2][i].value[3].keyIns, "lin_color": features[2][i].value[3].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[2][i*12+3]), "MI_pick":colorsScaleNodes(MIVar3[features[4].length+i*12+3])},
              {"name": features[2][i].value[4].keyIns, "lin_color": features[2][i].value[4].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[2][i*12+4]), "MI_pick":colorsScaleNodes(MIVar3[features[4].length+i*12+4])},
              {"name": features[2][i].value[5].keyIns, "lin_color": features[2][i].value[5].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[2][i*12+5]), "MI_pick":colorsScaleNodes(MIVar3[features[4].length+i*12+5])},
              {"name": features[2][i].value[6].keyIns, "lin_color": features[2][i].value[6].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[2][i*12+6]), "MI_pick":colorsScaleNodes(MIVar3[features[4].length+i*12+6])},
              {"name": features[2][i].value[7].keyIns, "lin_color": features[2][i].value[7].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[2][i*12+7]), "MI_pick":colorsScaleNodes(MIVar3[features[4].length+i*12+7])},
              {"name": features[2][i].value[8].keyIns, "lin_color": features[2][i].value[8].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[2][i*12+8]), "MI_pick":colorsScaleNodes(MIVar3[features[4].length+i*12+8])},
              {"name": features[2][i].value[9].keyIns, "lin_color": features[2][i].value[9].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[2][i*12+9]), "MI_pick":colorsScaleNodes(MIVar3[features[4].length+i*12+9])},
              {"name": features[2][i].value[10].keyIns, "lin_color": features[2][i].value[10].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[2][i*12+10]), "MI_pick":colorsScaleNodes(MIVar3[features[4].length+i*12+10])},
              {"name": features[2][i].value[11].keyIns, "lin_color": features[2][i].value[11].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[2][i*12+11]), "MI_pick":colorsScaleNodes(MIVar3[features[4].length+i*12+11])},
            ],
            "lin_color": features[2][i].value[0].valueIns+features[2][i].value[1].valueIns+features[2][i].value[2].valueIns+features[2][i].value[3].valueIns+features[2][i].value[4].valueIns+features[2][i].value[5].valueIns+features[2][i].value[6].valueIns+features[2][i].value[7].valueIns+features[2][i].value[8].valueIns+features[2][i].value[9].valueIns+features[2][i].value[10].valueIns+features[2][i].value[11].valueIns,
            "Corr_pick": Math.round(Object.values(corrGlob3)[i+1]['0'] * 100),
            "MI_pick": colorsScaleNodes(MIVar3[i])
            })
          featuresQuad4.push({"name": features[3][i].key,
            "children": [  
              {"name": features[3][i].value[0].keyIns, "lin_color": features[3][i].value[0].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[3][i*12+0]), "MI_pick":colorsScaleNodes(MIVar4[features[4].length+i*12+0])},
              {"name": features[3][i].value[1].keyIns, "lin_color": features[3][i].value[1].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[3][i*12+1]), "MI_pick":colorsScaleNodes(MIVar4[features[4].length+i*12+1])},
              {"name": features[3][i].value[2].keyIns, "lin_color": features[3][i].value[2].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[3][i*12+2]), "MI_pick":colorsScaleNodes(MIVar4[features[4].length+i*12+2])},
              {"name": features[3][i].value[3].keyIns, "lin_color": features[3][i].value[3].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[3][i*12+3]), "MI_pick":colorsScaleNodes(MIVar4[features[4].length+i*12+3])},
              {"name": features[3][i].value[4].keyIns, "lin_color": features[3][i].value[4].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[3][i*12+4]), "MI_pick":colorsScaleNodes(MIVar4[features[4].length+i*12+4])},
              {"name": features[3][i].value[5].keyIns, "lin_color": features[3][i].value[5].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[3][i*12+5]), "MI_pick":colorsScaleNodes(MIVar4[features[4].length+i*12+5])},
              {"name": features[3][i].value[6].keyIns, "lin_color": features[3][i].value[6].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[3][i*12+6]), "MI_pick":colorsScaleNodes(MIVar4[features[4].length+i*12+6])},
              {"name": features[3][i].value[7].keyIns, "lin_color": features[3][i].value[7].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[3][i*12+7]), "MI_pick":colorsScaleNodes(MIVar4[features[4].length+i*12+7])},
              {"name": features[3][i].value[8].keyIns, "lin_color": features[3][i].value[8].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[3][i*12+8]), "MI_pick":colorsScaleNodes(MIVar4[features[4].length+i*12+8])},
              {"name": features[3][i].value[9].keyIns, "lin_color": features[3][i].value[9].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[3][i*12+9]), "MI_pick":colorsScaleNodes(MIVar4[features[4].length+i*12+9])},
              {"name": features[3][i].value[10].keyIns, "lin_color": features[3][i].value[10].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[3][i*12+10]), "MI_pick":colorsScaleNodes(MIVar4[features[4].length+i*12+10])},
              {"name": features[3][i].value[11].keyIns, "lin_color": features[3][i].value[11].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[3][i*12+11]), "MI_pick":colorsScaleNodes(MIVar4[features[4].length+i*12+11])},
            ],
            "lin_color": features[3][i].value[0].valueIns+features[3][i].value[1].valueIns+features[3][i].value[2].valueIns+features[3][i].value[3].valueIns+features[3][i].value[4].valueIns+features[3][i].value[5].valueIns+features[3][i].value[6].valueIns+features[3][i].value[7].valueIns+features[3][i].value[8].valueIns+features[3][i].value[9].valueIns+features[3][i].value[10].valueIns+features[3][i].value[11].valueIns,
            "Corr_pick": Math.round(Object.values(corrGlob4)[i+1]['0'] * 100),
            "MI_pick": colorsScaleNodes(MIVar4[i])
            })
          featuresQuad5.push({"name": features[4][i].key,
            "children": [  
              {"name": features[4][i].value[0].keyIns, "lin_color": features[4][i].value[0].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[4][i*12+0]), "MI_pick":colorsScaleNodes(MIVar5[features[4].length+i*12+0])},
              {"name": features[4][i].value[1].keyIns, "lin_color": features[4][i].value[1].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[4][i*12+1]), "MI_pick":colorsScaleNodes(MIVar5[features[4].length+i*12+1])},
              {"name": features[4][i].value[2].keyIns, "lin_color": features[4][i].value[2].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[4][i*12+2]), "MI_pick":colorsScaleNodes(MIVar5[features[4].length+i*12+2])},
              {"name": features[4][i].value[3].keyIns, "lin_color": features[4][i].value[3].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[4][i*12+3]), "MI_pick":colorsScaleNodes(MIVar5[features[4].length+i*12+3])},
              {"name": features[4][i].value[4].keyIns, "lin_color": features[4][i].value[4].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[4][i*12+4]), "MI_pick":colorsScaleNodes(MIVar5[features[4].length+i*12+4])},
              {"name": features[4][i].value[5].keyIns, "lin_color": features[4][i].value[5].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[4][i*12+5]), "MI_pick":colorsScaleNodes(MIVar5[features[4].length+i*12+5])},
              {"name": features[4][i].value[6].keyIns, "lin_color": features[4][i].value[6].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[4][i*12+6]), "MI_pick":colorsScaleNodes(MIVar5[features[4].length+i*12+6])},
              {"name": features[4][i].value[7].keyIns, "lin_color": features[4][i].value[7].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[4][i*12+7]), "MI_pick":colorsScaleNodes(MIVar5[features[4].length+i*12+7])},
              {"name": features[4][i].value[8].keyIns, "lin_color": features[4][i].value[8].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[4][i*12+8]), "MI_pick":colorsScaleNodes(MIVar5[features[4].length+i*12+8])},
              {"name": features[4][i].value[9].keyIns, "lin_color": features[4][i].value[9].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[4][i*12+9]), "MI_pick":colorsScaleNodes(MIVar5[features[4].length+i*12+9])},
              {"name": features[4][i].value[10].keyIns, "lin_color": features[4][i].value[10].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[4][i*12+10]), "MI_pick":colorsScaleNodes(MIVar5[features[4].length+i*12+10])},
              {"name": features[4][i].value[11].keyIns, "lin_color": features[4][i].value[11].valueIns, "Corr_pick": Math.round(this.overallDataTransfCorr[4][i*12+11]), "MI_pick":colorsScaleNodes(MIVar5[features[4].length+i*12+11])},
            ],
            "lin_color": features[4][i].value[0].valueIns+features[4][i].value[1].valueIns+features[4][i].value[2].valueIns+features[4][i].value[3].valueIns+features[4][i].value[4].valueIns+features[4][i].value[5].valueIns+features[4][i].value[6].valueIns+features[4][i].value[7].valueIns+features[4][i].value[8].valueIns+features[4][i].value[9].valueIns+features[4][i].value[10].valueIns+features[4][i].value[11].valueIns,
            "Corr_pick": Math.round(Object.values(corrGlob5)[i+1]['0'] * 100),
            "MI_pick": colorsScaleNodes(MIVar5[i])
            })
        }
        
        var spaceSlice1=0
        var spaceSlice2 = 0
        var spaceSlice3 = 0
        var spaceSlice4 = 0
        var spaceSlice5 = 0

        for (let i = 0; i < featuresQuad5.length; i++) {
          spaceSlice4 = spaceSlice4 + featuresQuad4[i].lin_color
          spaceSlice5 = spaceSlice5 + featuresQuad5[i].lin_color
          spaceSlice1 = spaceSlice1 + featuresQuad1[i].lin_color
          spaceSlice2 = spaceSlice2 + featuresQuad2[i].lin_color
          spaceSlice3 = spaceSlice3 + featuresQuad3[i].lin_color
        }

        var treeData = {
          "name": "Data",
           "children": [  
              {"name": "Worst",
                "children": featuresQuad4,
                "lin_color": spaceSlice4
              },
              {"name": "All",
                "children": featuresQuad5,
                "lin_color": spaceSlice5
              },
              {"name": "Best",
              "children": featuresQuad1,
              "lin_color": spaceSlice1
              },
              {"name": "Good",
                "children": featuresQuad2,
                "lin_color": spaceSlice2
              },
              {"name": "Bad",
              "children": featuresQuad3,
              "lin_color": spaceSlice3
              },
            ]
        }

        var DURATION = 700; // d3 animation duration
        var STAGGERN = 4; // delay for each node
        var STAGGERD = 200; // delay for each depth
        var NODE_DIAMETER = 10; // diameter of circular nodes
        var MIN_ZOOM = 0.5; // minimum zoom allowed
        var MAX_ZOOM = 10;  // maximum zoom allowed
        var HAS_CHILDREN_COLOR = 'lightsteelblue';
        var SELECTED_COLOR = 'black';  // color of selected node
        var ZOOM_INC = 0.04;  // zoom factor per animation frame
        var PAN_INC = 3;  //  pan per animation frame
        var ROT_INC = 0.3;  // rotation per animation frame

        var counter = 0;  // node ids
        var curNode;  // currently selected node
        var curPath;  // array of nodes in the path to the currently selected node

        // size of the diagram
        var width = 820;
        var height = 820;

        // current pan, zoom, and rotation
        var curX = width / 2;
        var curY = height / 2;
        var curZ = 1.18; // current zoom
        var curR = 270; // current rotation

        // keyboard key codes
        var KEY_PLUS = 187;     // + (zoom in)
        var KEY_MINUS = 189;    // - (zoom out)
        var KEY_SLASH = 191;    // / (slash)
        var KEY_PAGEUP = 33;    // (rotate CCW)
        var KEY_PAGEDOWN = 34;  // (rotate CW)
        var KEY_LEFT = 37;      // left arrow
        var KEY_UP = 38;        // up arrow
        var KEY_RIGHT = 39;     // right arrow
        var KEY_DOWN = 40;      // down arrow
        var KEY_SPACE = 32;     // (expand node)
        var KEY_RETURN = 13;    // (expand tree)
        var KEY_HOME = 36;      // (center root)
        var KEY_END = 35;       // (center selection)

        // d3 diagonal projection for use by the node paths
        var diagonal= d3.svg.diagonal.radial()
          .projection(function(d) {
              return [d.y, d.x / 180 * Math.PI];
          });

        // d3 tree layout
        var tree = d3.layout.tree()
          // .nodeSize([4.5, 120])
          .size([360, Math.min(width, height) / 2 - 120])
          .separation(function(a, b) {
            return a.depth === 0 ? 1 : (a.parent === b.parent ? 1 : 2) / a.depth;
        });

        // define the svgBase, attaching a class for styling and the zoomListener
        var svgBase = d3.select('#tree-container').append('svg')
          .attr('width', width)
          .attr('height', height)
          .on('mousedown', mousedown);

        // Group which holds all nodes and manages pan, zoom, rotate
        var svgGroup = svgBase.append('g')
          .attr('transform', 'translate(' + curX + ',' + curY + ')');

        d3.select(document) // set up document events
          //.on('wheel', wheel)  // zoom, rotate
          .on('keydown', keydown)
          .on('keyup', keyup);
        d3.select(window).on('resize', resize);
        d3.selectAll('.button')
          .on('mousedown', tooldown)
          .on('mouseup', toolup);
        d3.select('#selection').on('mousedown', switchroot);
        d3.select('#contextmenu').on('mouseup', menuSelection);

        // Define the data root
        var root = treeData;
        root.x0 = curY;
        root.y0 = 0;
        selectNode(treeData.children[this.keepRoot]); // current selected node

        // Collapse all children of root's children before rendering

        root.children.forEach(function(child) {
          child.children.forEach(function(child) {
            collapseTree(child)
          });
        });

        root.children.forEach(function(child) {
          child.children.forEach(function(child) {
            if (child.name == listofNodes[activeLeafLoc]) {
              toggle(child)
            }
          });
        });  
        
        // root.children.forEach(function(child) {
        //   console.log(child)
        //   expand1Level(child)
        // });

        update(root, true); // Layout the tree initially and center on the root node
        // update the tree
        // source - source node of the update
        // transition - whether to do a transition
        function update(source, transition) {

          var duration = transition ?
            (d3.event && d3.event.altKey ? DURATION * 4 : DURATION) : 0;

          // Compute the new tree layout.
          var nodes = tree.nodes(root);
          var links = tree.links(nodes);

          // Update the view
          svgGroup.transition().duration(duration)
            .attr('transform',
              'rotate(' + curR + ' ' + curX + ' ' + curY +
              ')translate(' + curX + ' ' + curY +
              ')scale(' + curZ + ')');

          // Update the nodes…
          var node = svgGroup.selectAll('g.node')
            .data(nodes, function(d) {
              return d.id || (d.id = ++counter);
            });
            
          // Enter any new nodes at the parent's previous position
          var nodeEnter = node.enter().insert('g', ':first-child')
              .attr('class', 'node')
              .attr('transform', 'rotate(' + (source.x0 + 90) + ')translate(' + source.y0 + ')')
              .attr("id", function(d, i) { return "overCirc"+i })
              .on('click', click)
              .on('dblclick', dblclick)
              .on('contextmenu', showContextMenu);
              // .on('mousedown', suppress);

          //d3.select('#some-id').dispatch('click');

          nodeEnter.append('circle')
            .attr('r', 1e-6)
            .style('fill', function(d) {
              return d._children ? HAS_CHILDREN_COLOR : 'white';
            });

          nodeEnter.append('text')
            .text(function(d) {
              return d.name;
            })
            .style('opacity', 0.9)
            .style('fill-opacity', 0)
            .attr('transform', function() {
                return ((source.x0 + curR) % 360 <= 180 ?
                    'translate(8)scale(' :
                    'rotate(180)translate(-8)scale('
                  ) + reduceZ() + ')';
            });

          // update existing graph nodes

          // var linearGradient = node.append("defs")
          //   .append("linearGradient")
          //   .attr("id", function(d, i) { return "linear-gradient"+i });

          // linearGradient.append('stop')
          //   .attr('offset', function (d) {
          //       return '0%'
          //   })
          //   .attr('stop-color', function (d) {
          //     if (d.name == 'Data') {
          //       return 'white'
          //     } else if (d.name == 'All' || d.name == 'Best' || d.name == 'Good' || d.name == 'Bad' || d.name == 'Worst') {
          //       return '#D3D3D3'
          //     } else {
          //       return d.MI_pick
          //     }
          //   })
          //   .attr('stop-opacity', '1.0')
            
          // linearGradient.append('stop')
          //   .attr('offset', function (d) {
          //     if (d.name == 'Data' || d.name == 'All' || d.name == 'Best' || d.name == 'Good' || d.name == 'Bad' || d.name == 'Worst') {
          //       return '50%'
          //     } else {
          //       var result = String(d.Corr_pick)+'%'
          //       return result
          //     }
          //   })
          //   .attr('stop-color', function (d) {
          //     if (d.name == 'Data') {
          //       return 'white'
          //     } else if (d.name == 'All' || d.name == 'Best' || d.name == 'Good' || d.name == 'Bad' || d.name == 'Worst') {
          //       return '#D3D3D3'
          //     } else {
          //       var result = d.Corr_pick
          //       if (result >= 50)
          //         return d.MI_pick
          //       else
          //         return '#D3D3D3'
          //     }
          //   })
          //   .attr('stop-opacity', '1.0')

          // linearGradient.append('stop')
          //   .attr('offset', function (d) {
          //       return '100%'
          //   })
          //   .attr('stop-color', function (d) {
          //     if (d.name == 'Data') {
          //       return 'white'
          //     } else if (d.name == 'All' || d.name == 'Best' || d.name == 'Good' || d.name == 'Bad' || d.name == 'Worst') {
          //       return '#D3D3D3'
          //     } else {
          //       return '#D3D3D3'
          //     }
          //   })
          //   .attr('stop-opacity', '1.0')

          // Change the circle fill depending on whether it has children and is collapsed
          node.select('circle') 
            .attr('r', NODE_DIAMETER * reduceZ())
            .style('fill', function(d) {
                if (d.name == 'Data') {
                  return d._children ? 'white' : 'white';
                } else if (d.name == 'All') {
                  return d._children ? 'yellow' : 'yellow';
                } else if (d.name == 'Best') {
                  return d._children ? 'yellow' : 'yellow';
                } else if (d.name == 'Good') {
                  return d._children ? 'yellow' : 'yellow';
                } else if (d.name == 'Bad') {
                  return d._children ? 'yellow' : 'yellow';
                } else if (d.name == 'Worst') {
                  return d._children ? 'yellow' : 'yellow';
                } else {
                  if (activeLeafLoc != -1) {
                    if (d.name == listofNodes[activeLeafLoc]) {
                      return d._children ? '#969696' : '#969696'
                    }
                    else {
                      return d._children ? '#D3D3D3' : '#D3D3D3'
                    }
                  } else {
                    return d._children ? '#D3D3D3' : '#D3D3D3'
                  }
                }
            }).attr('stroke', function(d, i) {
              if(d.name == 'Data') {
                return d.selected ? SELECTED_COLOR : 'white';
              } else if (d.name == 'All' || d.name == 'Best' || d.name == 'Good' || d.name == 'Bad' || d.name == 'Worst') {
                return d.selected ? SELECTED_COLOR : '#D3D3D3';
              } else {
                return d.selected ? SELECTED_COLOR : "url(#linear-gradient"+i+")";
              }
            }).attr('stroke-width', function(d) {
              if(d.name == 'Data') {
                return d.selected ? 0 : 0;
              } else if (d.name == 'All' || d.name == 'Best' || d.name == 'Good' || d.name == 'Bad' || d.name == 'Worst'){
                return d.selected ? 4 : 4;
              } else {
                return d.selected ? 0 : 0;
              } 
            })

          node.select('text')
            .attr('text-anchor', function(d) {
                return (d.x + curR) % 360 <= 180 ? 'start' : 'end';
            }).attr('transform', function(d) {
                return ((d.x + curR) % 360 <= 180 ?
                    'translate(12)scale(' :
                    'rotate(180)translate(-12)scale('
                  ) + reduceZ() +')';
            }).attr('fill', function(d) {
                return d.selected ? 'black' : 'black';
            }).attr('dy', '.35em');

            var widthLoc = 4;
            var arcSize = (2.7 * widthLoc / 4);
            var innerRadius = arcSize * 3.2; 
            
            nodes.forEach(function(obj, index) {
              if (obj.name == 'Data' || obj.name == 'All' || obj.name == 'Best' || obj.name == 'Good' || obj.name == 'Bad' || obj.name == 'Worst') {
                if (firstTime) {
                  storeRootIndices.push(index)
                }
              } else {
                  var i = 0
                  var arcs = d3v5.arc().innerRadius(i * arcSize + innerRadius + 0.4).outerRadius((i + 1) * arcSize - (widthLoc / 4) + innerRadius);
                  
                  var arcsGrey = d3v5.arc().innerRadius(i * arcSize + (innerRadius + ((arcSize / 2) - 2)) + 0.4).outerRadius((i + 1) * arcSize - ((arcSize / 2)) + (innerRadius));

                  var pieData = [[{value: obj.Corr_pick, arc: arcs, object: obj},
                          {value: (100 - obj.Corr_pick), arc: arcsGrey, object: obj},
                          {value: 0, arc: arcs, object: obj}]]

                  var pie = d3v5.pie().sort(null).value(function (d) {
                      return d.value;
                  });
                  if (storeRootIndices.includes(index)) {

                  } else {
                      var g = d3v5.select('#overCirc'+index).selectAll('g').data(pieData).enter()
                      .append('g')
                      .attr('transform', function(d, i) {
                        return 'rotate(270)'
                      });

                    g.selectAll('path').data(function (d) {
                        return pie(d);
                    }).enter().append('path')
                        .attr('d', function (d) {
                            return d.data.arc(d);
                        }).attr('fill', function (d, i) {
                        if (i == 0) {
                          return d.data.object.MI_pick 
                        } else {
                          return '#D3D3D3'
                        }
                    });                
                  }

              }
            })
            
          firstTime = false

          var nodeUpdate = node.transition().duration(duration)
            .delay( transition ? function(d, i) {
                return i * STAGGERN +
                  Math.abs(d.depth - curNode.depth) * STAGGERD; }  : 0)
            .attr('transform', function(d) {
                return 'rotate(' + (d.x - 90) + ')translate(' + d.y + ')';
            });

          nodeUpdate.select('circle')
            .attr('r', NODE_DIAMETER * reduceZ());
            // .style('fill', function(d) {
            //   return d._children ? HAS_CHILDREN_COLOR : 'white';
            // });

          nodeUpdate.select('text')
            .style('fill-opacity', 1);

          // Transition exiting nodes to the parent's new position and remove
          var nodeExit = node.exit().transition().duration(duration)
            .delay( transition ? function(d, i) {
                return i * STAGGERN; } : 0)
            .attr('transform', function() {
              return 'rotate(' + (source.x - 90) +')translate(' + source.y + ')';
          }).remove();

          nodeExit.select('circle').attr('r', 0);
          nodeExit.select('text').style('fill-opacity', 0);

          // Update the links…
          var link = svgGroup.selectAll('path.link')
            .data(links, function(d) {
              return d.target.id;
            });

          // Enter any new links at the parent's previous position
          link.enter().insert('path', 'g')
              .attr('class', 'link')
              .attr('d', function() {
              var o = {
                  x: source.x0,
                  y: source.y0
              };
              return diagonal({
                  source: o,
                  target: o
              });
          }).style("stroke", function(d){
            if (d.target.lin_color > 0) {
              return '#33a02c'
            } else if (d.target.lin_color < 0) {
              return '#e31a1c'
            } else {
              return '#D3D3D3'
            }
          })

          // Transition links to their new position
          link.transition().duration(duration)
            .delay( transition ? function(d, i) {
                return i * STAGGERN +
                  Math.abs(d.source.depth - curNode.depth) * STAGGERD;
                  // Math.max(0, d.source.depth - curNode.depth) * STAGGERD;
                } : 0)
            .attr('d', diagonal);

          // Transition exiting nodes to the parent's new position
          link.exit().transition().duration(duration)
              .attr('d', function() {
                var o = {
                  x: source.x0,
                  y: source.y0
                };
                return diagonal({
                  source: o,
                  target: o
                });
            }).remove();

          // Stash the old positions for transition
          nodes.forEach(function(d) {
            d.x0 = d.x;
            d.y0 = d.y;
          });
        } // end update

        // Helper functions for collapsing and expanding nodes

        // Toggle expand / collapse
        function toggle(d) {
          if (d.children) {
            d._children = d.children;
            d.children = null;
          } else if (d._children) {
            d.children = d._children;
            d._children = null;
          }
        }

        function toggleTree(d) {
          if (d.children) {
            collapseTree(d);
          } else {
            expandTree(d);
          }
        }

        function expand(d) {
          if (d._children) {
            d.children = d._children;
            d._children = null;
          }
        }

        // expand all children, whether expanded or collapsed
        function expandTree(d) {
          if (d._children) {
            d.children = d._children;
            d._children = null;
          }
          if (d.children) {
            d.children.forEach(expandTree);
          }
        }

        function collapse(d) {
          if (d.children) {
            d._children = d.children;
            d.children = null;
          }
        }

        // collapse all children
        function collapseTree(d) {
          if (d.children) {
            d._children = d.children;
            d.children = null;
          }
          if (d._children) {
            d._children.forEach(collapseTree);
          }
        }

        // expand one level of tree
        function expand1Level(d) {
          var q = [d]; // non-recursive
          var cn;
          var done = null;
          while (q.length > 0) {
            cn = q.shift();
            if (done !== null && done < cn.depth) { return; }
            if (cn._children) {
              done = cn.depth;
              cn.children = cn._children;
              cn._children = null;
              cn.children.forEach(collapse);
            }
            if (cn.children) { q = q.concat(cn.children); }
          }
          // no nodes to open
        }

        // highlight selected node
        function selectNode(node) {
          if (curNode) {
            delete curNode.selected;
          }
          curNode = node;
          curNode.selected = true;
          curPath = []; // filled in by fullpath
          d3.select('#selection').html(fullpath(node));
        }

        // for displaying full path of node in tree
        function fullpath(d, idx) {
          idx = idx || 0;
          curPath.push(d);
          return '/<span class="nodepath'+
            '" data-sel="'+ idx +'" title="Set Root to '+ d.name +'">' +
            d.name + '</span>';
        }

        // d3 event handlers

        function switchroot() {
          d3.event.preventDefault();
          var pathelms = document.querySelectorAll('#selection .nodepath');
          for (var i = 0; i < pathelms.length; i++) {
            //pathelms[i].classList.remove('highlight');
          }
          var target = d3.event.target;
          var node = curPath[+target.dataset.sel];
          if (d3.event.shiftKey) {
            if (curNode !== node) {
              selectNode(node);
            }
          } else {
            root = node;
            target.classList.add('highlight');
          }
          update(root, true);
        }

        function resize() { // window resize
          var oldwidth = width;
          var oldheight = height;
          width = window.innerWidth - 20;
          height = window.innerHeight - 20;
          tree.size([360, Math.min(width, height) / 2 - 120]);
          svgBase.attr('width', width).attr('height', height);
          curX += (width - oldwidth) / 2;
          curY += (height - oldheight) / 2;
          svgGroup.attr('transform', 'rotate(' + curR + ' ' + curX + ' ' + curY +
              ')translate(' + curX + ' ' + curY + ')scale(' + curZ + ')');
          update(root);
        }
        
        function click(d) { // select node
          if (d3.event.defaultPrevented || d === curNode) { return; } // suppressed
          d3.event.preventDefault();
          selectNode(d);
          update(d);
          var sendSliceID = 4
          var rootID = 1
          if (d.name == "Best") {
            sendSliceID = 0
            rootID = 2
          } else if (d.name == "Good") {
            sendSliceID = 1
            rootID = 3
          } else if (d.name == "Bad") {
            sendSliceID = 2
            rootID = 4
          } else if (d.name == "Worst") {
            sendSliceID = 3
            rootID = 0
          } else {
            sendSliceID = 4
            rootID = 1
          }
          EventBus.$emit('flagSpace', true)
          EventBus.$emit('keepRootFun', rootID)
          EventBus.$emit('updateSlice', sendSliceID)
        }

        function dblclick(d, i) {  // Toggle children of node
          if (d3.event.defaultPrevented) { return; } // click suppressed
          d3.event.preventDefault();
          if (d3.event.shiftKey) {
            expand1Level(d); // expand node by one level
          } else {
            
            if (d.children) {
              EventBus.$emit('collapsedNode', d.name)
            } else if (d._children) {
              EventBus.$emit('expandedNode', d.name)
            }

            toggle(d);
          }
          update(d, true);
        }



        function tooldown(d) {  // tool button pressed
          d3.event.preventDefault();
          d3.select(d3.event.target).on('mouseout', toolup);
          var key = +d3.event.target.dataset.key;
          keydown(Math.abs(key), key < 0 || d3.event.shiftKey);
        }

        function toolup() {  // tool button released
          d3.event.preventDefault();
          d3.select(d3.event.target).on('mouseout', null);
          keyup(Math.abs(+d3.event.target.dataset.key));
        }

        // right click, show context menu and select this node
        function showContextMenu(d) {
          d3.event.preventDefault();
          d3.selectAll('.expcol').text(d.children ? 'Collapse' : 'Expand');
          d3.select('#contextmenu').style({
            left: (d3.event.pageX + 3) + 'px',
            top: (d3.event.pageY + 8) + 'px',
            display: 'block'
          });
          d3.select(document).on('mouseup', hideContextMenu);
          selectNode(d);
          update(d);
        }

        function hideContextMenu() {
          d3.select('#contextmenu').style('display', 'none');
          d3.select(document).on('mouseup', null);
        }

        function menuSelection() {
          d3.event.preventDefault();
          var key = +d3.event.target.dataset.key;
          keydown(Math.abs(key), key < 0 || d3.event.shiftKey);
        }

        var startposX, startposY; // initial position on mouse button down for pan

        function mousedown() {  // pan
          d3.event.preventDefault();
          if (d3.event.which !== 1 || d3.event.ctrlKey) { return; } // ingore other mouse buttons
          startposX = curX - d3.event.clientX;
          startposY = curY - d3.event.clientY;
          d3.select(document).on('mousemove', mousemove, true);
          d3.select(document).on('mouseup', mouseup, true);
        }

        function mousemove() {
          d3.event.preventDefault();
          curX = startposX + d3.event.clientX;
          curY = startposY + d3.event.clientY;
          setview();
        }

        function mouseup() {
          d3.select(document).on('mousemove', null);
          d3.select(document).on('mouseup', null);
        }

        var keysdown = [];  // which keys are currently down
        var moveX = 0, moveY = 0, moveZ = 0, moveR = 0; // animations
        var aniRequest = null;

        // function wheel() {  // mousewheel
        //   var dz, newZ;
        //   var slow = d3.event.altKey ? 0.25 : 1;
        //   if (d3.event.wheelDeltaY !== 0) {  // up-down
        //     dz = Math.pow(1.2, d3.event.wheelDeltaY * 0.001 * slow);
        //     newZ = limitZ(curZ * dz);
        //     dz = newZ / curZ;
        //     curZ = newZ;

        //     curX -= (d3.event.clientX - curX) * (dz - 1);
        //     curY -= (d3.event.clientY - curY) * (dz - 1);
        //     setview();
        //   }
        //   if (d3.event.wheelDeltaX !== 0) {  // left-right
        //     curR = limitR(curR + d3.event.wheelDeltaX * 0.01 * slow);
        //     update(root);
        //   }
        // }

        if(this.collapsed.length != 0) {
          console.log(this.collapsed)
          root.children.forEach(element => {
            if (this.collapsed.includes(element.name)) {
              toggle(element);
              update(element, true);
            }
          });
        }

        // keyboard shortcuts
        function keydown(key, shift) {
          if (!key) {
            key = d3.event.which;  // fake key
            shift = d3.event.shiftKey;
          }
          var parch; // parent's children
          var slow = d3.event.altKey ? 0.25 : 1;
          if (keysdown.indexOf(key) >= 0) { return; } // defeat auto repeat
          switch (key) {
            case KEY_PLUS: // zoom in
              moveZ = ZOOM_INC * slow;
              break;
            case KEY_MINUS: // zoom out
              moveZ = -ZOOM_INC * slow;
              break;
            case KEY_SLASH: // toggle root to selection
              root = root === curNode ? treeData : curNode;
              update(root, true);
              curPath = []; // filled in by fullpath
              d3.select('#selection').html(fullpath(curNode));
              return;
            case KEY_PAGEUP: // rotate counterclockwise
              moveR = -ROT_INC * slow;
              break;
            case KEY_PAGEDOWN: // zoom out
              moveR = ROT_INC * slow; // rotate clockwise
              break;
            case KEY_LEFT: // left arrow
              if (shift) { // move selection to parent
                if (!curNode) {
                  selectNode(root);
                } else if (curNode.parent) {
                  selectNode(curNode.parent);
                }
                update(curNode);
                return;
              }
              moveX = -PAN_INC * slow;
              break;
            case KEY_UP: // up arrow
              if (shift) { // move selection to previous child
                if (!curNode) {
                  selectNode(root);
                } else if (curNode.parent) {
                  parch = curNode.parent.children;
                  selectNode(parch[(parch.indexOf(curNode) +
                      parch.length - 1) % parch.length]);
                }
                update(curNode);
                return;
              }
              moveY = -PAN_INC * slow;
              break;
            case KEY_RIGHT: // right arrow
              if (shift) { // move selection to first/last child
                if (!curNode) {
                  selectNode(root);
                } else {
                  if (curNode.children) {
                    selectNode(curNode.children[d3.event.altKey ?
                        curNode.children.length - 1 : 0]);
                  }
                }
                update(curNode);
                return;
              }
              moveX = PAN_INC * slow;
              break;
            case KEY_DOWN: // down arrow
              if (shift) { // move selection to next child
                if (!curNode) {
                  selectNode(root);
                } else if (curNode.parent) {
                  parch = curNode.parent.children;
                  selectNode(parch[(parch.indexOf(curNode) + 1) % parch.length]);
                }
                update(curNode);
                return;
              }
              moveY = PAN_INC * slow;
              break;
            case KEY_SPACE: // expand/collapse node
              if (!curNode) {
                selectNode(root);
              }
              toggle(curNode);
              update(curNode, true);
              return;
            case KEY_RETURN: // expand/collapse tree
              if (!curNode) {
                selectNode(root);
              }
              if (shift) {
                expandTree(curNode);
              } else {
                expand1Level(curNode);
              }
              update(curNode, true);
              return;
            case KEY_HOME: // reset transform
              if (shift) {
                root = treeData;
              }
              curX = width / 2;
              curY = height / 2;
              curR = limitR(90 - root.x);
              curZ = 1;
              update(root, true);
              return;
            case KEY_END: // zoom to selection
              if (!curNode) { return; }
              curX = width / 2 - curNode.y * curZ;
              curY = height / 2;
              curR = limitR(90 - curNode.x);
              update(curNode, true);
              return;
            default: return;  // ignore other keys
          } // break jumps to here
          keysdown.push(key);
          // start animation if anything happening
          if (keysdown.length > 0 && aniRequest === null) {
            aniRequest = requestAnimationFrame(frame);
          }
        }

        function keyup(key) {
          key = key || d3.event.which;
          var pos = keysdown.indexOf(key);
          if (pos < 0) { return; }

          switch (key) {
            case KEY_PLUS: // zoom out
            case KEY_MINUS: // zoom in
              moveZ = 0;
              break;
            case KEY_PAGEUP: // rotate CCW
            case KEY_PAGEDOWN: // rotate CW
              moveR = 0;
              break;
            case KEY_LEFT: // left arrow
            case KEY_RIGHT: // right arrow
              moveX = 0;
              break;
            case KEY_UP: // up arrow
            case KEY_DOWN: // down arrow
              moveY = 0;
              break;
          }
          keysdown.splice(pos, 1);  // remove key
          if (keysdown.length > 0 || aniRequest === null) { return; }
          cancelAnimationFrame(aniRequest);
          aniRequest = aniTime = null;
        }

        var aniTime = null;

        // update animation frame
        function frame(frametime) {
          var diff = aniTime ? (frametime - aniTime) / 16 : 0;
          aniTime = frametime;

          var dz = Math.pow(1.2, diff * moveZ);
          var newZ = limitZ(curZ * dz);
          dz = newZ / curZ;
          curZ = newZ;
          curX += diff * moveX - (width / 2- curX) * (dz - 1);
          curY += diff * moveY - (height / 2 - curY) * (dz - 1);
          curR = limitR(curR + diff * moveR);
          setview();
          aniRequest = requestAnimationFrame(frame);
        }

        // enforce zoom extent
        function limitZ(z) {
          return Math.max(Math.min(z, MAX_ZOOM), MIN_ZOOM);
        }

        // keep rotation between 0 and 360
        function limitR(r) {
          return (r + 360) % 360;
        }

        // limit size of text and nodes as scale increases
        function reduceZ() {
          return Math.pow(1.1, -curZ);
        }

        // set view with no animation
        function setview() {
            svgGroup.attr('transform', 'rotate(' + curR + ' ' + curX + ' ' + curY +
                ')translate(' + curX + ' ' + curY + ')scale(' + curZ + ')');
            svgGroup.selectAll('text')
                .attr('text-anchor', function(d) {
                    return (d.x + curR) % 360 <= 180 ? 'start' : 'end';
                })
                .attr('transform', function(d) {
                    return ((d.x + curR) % 360 <= 180 ?
                        'translate(12)scale(' :
                        'rotate(180)translate(-12)scale('
                      ) + reduceZ() +')';
                });
            svgGroup.selectAll('circle').attr('r', NODE_DIAMETER * reduceZ());
        }
        
        var legendRectSize = 14;                                
        var legendSpacing = 3;         
        var labelsData = JSON.parse(this.overallData[1])                         
        var color = d3v5.scaleOrdinal().domain(labelsData).range(['#808000','#7570b3','#469990'])

        var svgLegend = d3v5.select('#legendTarget').append('svg')                    
            .attr('width', 130)
            .attr('height', 60)               

        var legend = svgLegend.selectAll('.legend')                     // NEW
          .data(labelsData)                                       // NEW
          .enter()                                                // NEW
          .append('g')                                            // NEW
          .attr('class', 'legend')                                // NEW
          .attr('transform', function(d, i) {                     // NEW
            var height = legendRectSize + legendSpacing;          // NEW
            var offset =  height * 0 / 2;
            var horz = 25     // NEW
            var vert = i * height - offset;                       // NEW
            return 'translate(' + horz + ',' + vert + ')';        // NEW
          });                                                     // NEW

        legend.append('rect')                                    
          .attr('width', legendRectSize)               
          .attr('height', legendRectSize)                     
          .style('fill', function (d) { return color(d) })
          .style('opacity', "0.5");             
          
        legend.append('text')   
          .attr('class', 'legendLab')                               
          .attr('x', legendRectSize + legendSpacing)       
          .attr('y', legendRectSize - legendSpacing)      
          .text(function(d) { return d; });       
      }
    },
  mounted () {

    EventBus.$on('expandedNode', data => {
      const index = this.collapsed.indexOf(data);
      if (index > -1) {
        this.collapsed.splice(index, 1);
      }
    })
    EventBus.$on('collapsedNode', data => {
       if(this.collapsed.includes(data)) {
         
       } else {
        this.collapsed.push(data) 
       }
    })

    EventBus.$on('keepRootFun', data => { this.keepRoot = data })
    EventBus.$on('quad', data => { this.overallData = data })

    EventBus.$on('overviewCallCorrTotal', data => { this.overallDataTransfCorr = data })
    EventBus.$on('overviewCallMI', data => { this.overallDataTransfMI = data })

    EventBus.$on('overviewCall', data => { this.colorsReceive = data })
    EventBus.$on('overviewCall', this.initializeRadialTree)

    EventBus.$on('brushLink', data => { this.activeLeaf = data })
    EventBus.$on('brushLink', this.initializeRadialTree)

    EventBus.$on('reset', this.reset)
  }
}
</script>

<style>

text {
  font-family: sans-serif;
}

svg {
  display: block;
}

#toolbar {
  display: -webkit-box;
  display: moz-box-flex;
  display: -ms-flexbox;
  display: -webkit-flex;
  flex-wrap: wrap;
  top: 10px;
  margin-top: 25px;
  left: 10px;
  font-family: sans-serif;
  box-shadow: 1px 1px 3px;
  background-color: #ECEFF1;
}
.tool {
  display: flex;
  flex-direction: column;
  border: solid black 1px;
  padding: 1px;
}
.tlabel {
  text-align: center;
  padding: 3px 2px 1px 2px;
}
.tbuttons {
  display: flex;
  display: -webkit-box;
  display: moz-box-flex;
  display: -ms-flexbox;
  display: -webkit-flex;
  flex-wrap: wrap;
  flex-direction: row;
}
.button {
  border: outset gray 2px;
	border-radius: 4px;
	cursor: pointer;
  padding: 1px 3px;
  min-width: 12px;
  text-align: center;
  margin: 2px;
  font-family: "Courier New", Courier, monospace;
  background-color: white;
}
.button:hover {
  background-color: yellow;
}
.button:active {
  border: inset gray 2px;
}
#selection {
  margin: 2px 5px;
  vertical-align: middle;
  font-family: "Courier New", Courier, monospace;
  color: black;
  background-color: white;
}
#selection span.nodepath:hover {
  background-color: rgba(0, 0, 25, 0.1);
  cursor: pointer;
}
#selection span.nodepath.highlight {
  font-weight: bold;
}
#contextmenu {
  display: none;
  position: absolute;
  border: solid black 1px;
  box-shadow: 2px 2px 3px gray;
  padding: 2px;
  background-color: white;
  font-family: Roboto, Helvetica, sans-serif;
  font-size: 0.9em;
}
#contextmenu div {
  padding: 4px 10px;
  cursor: pointer;
}
#contextmenu div:hover {
  background-color: rgba(0, 0, 25, 0.1);
}
#contextmenu span.expcol {
  pointer-events: none;
}
#help {
  position: relative;
  bottom: -1.7em;
  transform: rotate(270deg);
  -webkit-transform: rotate(270deg);
  -moz-transform: rotate(270deg);
  -o-transform: rotate(270deg);
  width: 100px;
  text-align: center;
  margin-top: -6px;
  margin-left: -38px; 
}
#help a {
  color: black;
  text-decoration: none;
  background-color: white;
}
#help:hover a {
  background-color: yellow;
}

#tree-container, svg {
  overflow: hidden;
}
.node {
  cursor: pointer;
}
.node circle {
  fill: #fff;
}
.node text {
  font-size: 12px;
  font-family: Roboto, sans-serif;
  text-shadow: 4px 4px 3px white, -4px -4px 3px white;
}
.node text:hover {
  font-size: 1.2em;
  transition: font-size 0.1s;
}
.node text:not(:hover) {
  transition: font-size 1s;
  transition-delay: 0.5s;
}
.link {
  fill: none;
  stroke: #D3D3D3;
}

.legendLab {
  font-size: 14px !important;
}

#moveLabel { 
  position: absolute;
  transform: translate(1366px, -2px);
  z-index: 3;
  min-height: 68px;
  max-height: 68px;
}

#moveNavigate { 
  position: absolute;
  transform: translate(1292px, -2px);
  z-index: 3;
  min-height: 68px;
  max-height: 68px;
}

#selection {
  font-weight: bold;
}

</style>