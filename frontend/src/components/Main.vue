<!-- Main Visualization View -->

<template>
<body>
    <b-container fluid class="bv-example-row">
      <b-row class="md-3">
        <b-col cols="12">
          <mdb-card>
            <mdb-card-header color="primary-color" tag="h5" class="text-center"><DataSetSlider/></mdb-card-header>
            <mdb-card-body>
              <mdb-card-text class="text-left" style="font-size: 18.5px; min-height: 248px">
                <DataSpace/>
              </mdb-card-text>
            </mdb-card-body>
          </mdb-card>
        </b-col>
      </b-row>
      <b-row class="md-3">
        <b-col>
          <mdb-card style="margin-top: 15px;">
            <mdb-card-header color="primary-color" tag="h5" class="text-center"><font-awesome-icon icon="layer-group" style="margin-right: 5px"/>Feature Selection Techniques
              </mdb-card-header>
              <mdb-card-body>
                <mdb-card-text class="text-center"  style="min-height: 920px">
                  <Heatmap/>
                </mdb-card-text>
              </mdb-card-body>
          </mdb-card>
        </b-col>
          <b-col cols="4">
            <mdb-card style="margin-top: 15px;">
              <mdb-card-header color="primary-color" tag="h5" class="text-center">Feature Space Overview
                </mdb-card-header>
                <mdb-card-body>
                  <mdb-card-text class="text-center"  style="min-height: 920px">
                    <FeatureSpaceOverview/>
                  </mdb-card-text>
                </mdb-card-body>
            </mdb-card>
          </b-col>
          <b-col cols="4">
            <mdb-card style="margin-top: 15px;">
              <mdb-card-header color="primary-color" tag="h5" class="text-center">Feature Space Detail
              </mdb-card-header>
              <mdb-card-body>
                <mdb-card-text class="text-center"  style="min-height: 920px">
                  <FeatureSpaceDetail/>
                </mdb-card-text>
              </mdb-card-body>
            </mdb-card>
          </b-col>
          <b-col cols="2">
            <mdb-card style="margin-top: 15px;">
              <mdb-card-header color="primary-color" tag="h5" class="text-left">Process Tracker and Predictive Results 
              </mdb-card-header>
              <mdb-card-body>
                <mdb-card-text class="text-center"  style="min-height: 920px">
                  <Knowledge/>
                  <Results/>
                </mdb-card-text>
              </mdb-card-body>
            </mdb-card>
          </b-col>
        </b-row>
    </b-container>
  <div class="w3-container">
  <div id="myModal" class="w3-modal" style="position: fixed;">
    <div class="w3-modal-content w3-card-4 w3-animate-zoom">
      <header class="w3-container w3-blue"> 
      <h3 style="display:inline-block; font-size: 16px; margin-top: 15px; margin-bottom:15px">Serialized features using Cryo</h3>
      </header>
      <Export/>
      <div class="w3-container w3-light-grey w3-padding">
      <button style="float: right; margin-top: -3px; margin-bottom: -3px"
        id="closeModal" class="w3-button w3-right w3-white w3-border" 
        v-on:click="closeModalFun">
        <font-awesome-icon icon="window-close" />
        {{ valuePickled }}
        </button>
      </div>
      </div>
    </div>
  </div>
  </body>
</template>

<script>

import Vue from 'vue'
import DataSetSlider from './DataSetSlider.vue'
import DataSpace from './DataSpace.vue'
import FeatureSpaceOverview from './FeatureSpaceOverview.vue'
import FeatureSpaceDetail from './FeatureSpaceDetail.vue'
import Heatmap from './Heatmap.vue'
import Export from './Export.vue'
import Knowledge from './Knowledge.vue'
import Results from './Results.vue'
import axios from 'axios'
import { loadProgressBar } from 'axios-progress-bar'
import 'axios-progress-bar/dist/nprogress.css'
import 'bootstrap-css-only/css/bootstrap.min.css'
import { mdbCard, mdbCardBody, mdbCardText, mdbCardHeader } from 'mdbvue'
import { EventBus } from '../main.js'
import $ from 'jquery'; // <-to import jquery
import 'bootstrap';
import * as d3Base from 'd3'
import Papa from 'papaparse'

// attach all d3 plugins to the d3 library
const d3 = Object.assign(d3Base)

export default Vue.extend({
  name: 'Main',
  components: {
    DataSetSlider,
    DataSpace,
    FeatureSpaceOverview,
    FeatureSpaceDetail,
    Heatmap,
    Export,
    Knowledge,
    Results,
    mdbCard,
    mdbCardBody,
    mdbCardHeader,
    mdbCardText
  },
  data () {
    return {
      valuePickled: 'Close',
      transformNodesFlag: false,
      storeDataTransf: [],
      compareNumber: 0,
      IDToCompare: [],
      spaceChange: false,
      ImportanceCompare: [],
      featureNames: [],
      initAuto: true,
      keySlider: true,
      featureAddRem: [],
      featureAddRemGen: [],
      ValidResults: [],
      correlResulTranformed: [],
      PositiveValue: 75,
      NegativeValue: 25,
      unselectedRemainingPoints: [],
      Collection: 0,
      OverviewResults: 0,
      DataResults: '',
      keyNow: 1,
      instancesImportance: '',
      RetrieveValueFile: 'WineC', // this is for the default data set
      //RetrieveValueFile: 'VehicleC', // this is for the default data set
      SelectedFeaturesPerClassifier: '',
      FinalResults: 0,
      selectedAlgorithm: '',
      PerformancePerModel: '',
      PerformanceCheck: '',
      firstTimeFlag: 1,
      selectedModels_Stack: [],
      parametersofModels: [],
      reset: false,
      brushedBoxPlotUpdate: 0,
      width: 0,
      height: 0,
      combineWH: [],
      sumPerClassifier: [],
      valueSel: 0,
      valueAll: 0,
      OverSelLength: 0,
      OverAllLength: 0,
      OverSelLengthCM: 0,
      OverAllLengthCM: 0,
      modelsUpdate: [],
      AlgorithmsUpdate: [],
      SelectedMetricsForModels: [],
      DataPointsSel: '',
      DataPointsModels: '',
      dataPointsSelfromDataSpace: '',
      userSelectedFilterMain: 'mean',
      actionData: '',
      filterData: '',
      provenanceData: '',
      localFile: '',
      toggleDeepMain: 1,
      keyImp: true,
      ClassifierIDsListRemaining: [],
      PredictSel: []
    }
  },
  methods: {
    openModalFun () {
      $('#myModal').modal('show')
      this.requestTest()
    },
    closeModalFun () {
      $('#myModal').modal('hide')
    },
    requestTest () {
      const path = `http://127.0.0.1:5000/data/testResults`

      const postData = {
      }
      
      const axiosConfig = {
      headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
      'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS'
      }
      }
      axios.post(path, postData, axiosConfig)
      .then(response => {
        console.log('Execute Test Protocol!')
      })
      .catch(error => {
      console.log(error)
      })
    },
    openModalCalculate () {
      const path = `http://127.0.0.1:5000/data/RequestBestFeatures`

      const axiosConfig = {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
          'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS'
        }
      }
      axios.get(path, axiosConfig)
        .then(response => {
          var finalResultsData = JSON.parse(response.data.finalResultsData)
          EventBus.$emit('sendSelectedFeaturestoPickle', finalResultsData)
          console.log('Pickle data successful!')
        })
        .catch(error => {
          console.log(error)
        })
    },
    getCollection () {
      this.Collection = this.getCollectionFromBackend()
    },
    getCollectionFromBackend () {
      const path = `http://localhost:5000/data/ClientRequest`

      const axiosConfig = {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
          'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS'
        }
      }
      axios.get(path, axiosConfig)
        .then(response => {
          this.Collection = response.data.Collection
          EventBus.$emit('emittedEventCallingDataPlot', this.Collection)
          console.log('Collection was overwritten with new data sent by the server!')
        })
        .catch(error => {
          console.log(error)
        })
    },
    getDatafromtheBackEnd () {
      const path = `http://localhost:5000/data/PlotClassifiers`
      const axiosConfig = {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
          'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS'
        }
      }
      axios.get(path, axiosConfig)
        .then(response => {
          this.OverviewResults = response.data.OverviewResults
          console.log('Server successfully sent all the data related to visualizations!')
          EventBus.$emit('emittedEventCallingScatterPlot', this.OverviewResults)
          EventBus.$emit('emittedEventCallingGrid', this.OverviewResults)
          EventBus.$emit('emittedEventCallingGridSelection', this.OverviewResults)
          //this.getFinalResults()
        })
        .catch(error => {
          console.log(error)
        })
    },
    getCMComputedData () {
      const path = `http://localhost:5000/data/PlotCrossMutate`

      const axiosConfig = {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
          'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS'
        }
      }
      axios.get(path, axiosConfig)
        .then(response => {
          this.OverviewResultsCM = response.data.OverviewResultsCM
          console.log('Server successfully sent all the data related to visualizations!')
          EventBus.$emit('emittedEventCallingCrossoverMutation', this.OverviewResultsCM)
          //this.getFinalResults()
        })
        .catch(error => {
          console.log(error)
        })
    },
    SendToServerData () {
      const path = `http://127.0.0.1:5000/data/SendtoSeverDataSet`

      const postData = {
        uploadedData: this.localFile
      }
      const axiosConfig = {
      headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
      'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS'
      }
      }
      axios.post(path, postData, axiosConfig)
      .then(response => {
        console.log('Sent the new uploaded data to the server!')
      })
      .catch(error => {
      console.log(error)
      })
    },
    getFinalResultsFromBackend () {
      const path = `http://localhost:5000/data/SendFinalResultsBacktoVisualize`

      const axiosConfig = {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
          'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS'
        }
      }
      axios.get(path, axiosConfig)
        .then(response => {
          this.FinalResults = response.data.FinalResults
          EventBus.$emit('emittedEventCallingLinePlot', this.FinalResults)
        })
        .catch(error => {
          console.log(error)
        })
    },
    fileNameSend () {
      const path = `http://127.0.0.1:5000/data/ServerRequest`
      const postData = {
        fileName: this.RetrieveValueFile,
      }
      const axiosConfig = {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
          'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS'
        }
      }
      axios.post(path, postData, axiosConfig)
      .then(response => {
        console.log('File name was sent successfully!')
        this.threshold()
      })
      .catch(error => {
        console.log(error)
      })
    },
    Reset () {
      const path = `http://127.0.0.1:5000/data/Reset`
      this.reset = true
      const postData = {
        ClassifiersList: this.reset
      }
      const axiosConfig = {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
          'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS'
        }
      }
      axios.post(path, postData, axiosConfig)
        .then(response => {
          console.log('The server side was reset! Done.')
          this.reset = false
          EventBus.$emit('resetViews')
          this.fileNameSend()
        })
        .catch(error => {
          console.log(error)
        })
    },
    render (flag) {
      this.combineWH = []
      this.width = document.body.clientWidth / 12 - 30
      this.height = document.body.clientHeight / 3
      this.combineWH.push(this.width)
      this.combineWH.push(this.height)
      if(flag) {
        EventBus.$emit('Responsive', this.combineWH)
      }
      else {
        EventBus.$emit('ResponsiveandChange', this.combineWH)
      }
    },
    change () {
      this.render(false)
    },
    RetrieveNewColors () {
      const path = `http://127.0.0.1:5000/data/UpdateOverv`

      const axiosConfig = {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
          'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS'
        }
      }
      axios.get(path, axiosConfig)
        .then(response => {
          this.sumPerClassifierSel = response.data.Results
          console.log('Server successfully send the new colors!')
          EventBus.$emit('getColors',this.sumPerClassifierSel)
        })
        .catch(error => {
          console.log(error)
        })
    },
    threshold () {
      const path = `http://127.0.0.1:5000/data/thresholdDataSpace`
      const postData = {
        PositiveValue: this.PositiveValue,
        NegativeValue: this.NegativeValue
      }
      const axiosConfig = { 
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
          'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS'
        }
      }
      axios.post(path, postData, axiosConfig)
        .then(response => {
          console.log('Sent the thresholds to the server side!')
          this.returnCorrelTranformed()
        })
        .catch(error => {
          console.log(error)
        })
    },
    returnCorrelTranformed () {
    const path = `http://127.0.0.1:5000/data/returnCorrelationsTransformed`

    const axiosConfig = {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
        'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS'
      }
    }
    axios.get(path, axiosConfig)
      .then(response => {
        console.log('Server successfully send the correlation matrices!')
        this.correlResulTranformed = response.data.correlResulTranformed
        EventBus.$emit('quadTrans', this.correlResulTranformed)
        this.returnCorrel()
      })
      .catch(error => {
        console.log(error)
      })
  },
  returnCorrel () {
    const path = `http://127.0.0.1:5000/data/returnCorrelations`

    const axiosConfig = {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
        'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS'
      }
    }
    axios.get(path, axiosConfig)
      .then(response => {
        console.log('Server successfully send the correlation matrices!')
        this.correlResul = response.data.correlResul
        if (this.initAuto) {
          EventBus.$emit('dataSpace', this.correlResul)
          if (this.keySlider) {
            EventBus.$emit('SlidersCall')
            this.keySlider = false
          }
          // EventBus.$emit('ConfirmDataSet') // REMOVE THAT!
        } else {
          EventBus.$emit('dataSpace', this.correlResul)
          EventBus.$emit('quad', this.correlResul)
          if (this.keyImp) {
            this.returnImportance()
            this.keyImp = false
          } else {
            this.returnResults()
          }
        }
      })
      .catch(error => {
        console.log(error)
      })
  },
  returnImportance () {
    const path = `http://127.0.0.1:5000/data/sendFeatImp`
    
    const axiosConfig = {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
        'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS'
      }
    }
    axios.get(path, axiosConfig)
      .then(response => {
        console.log('Server successfully send the importances!')
        this.Importance = response.data.Importance
        this.featureNames = []
        EventBus.$emit('Generation', this.featureNames)
        EventBus.$emit('HeatmapCall', this.Importance)
        if (!this.transformNodesFlag) {
          this.returnResults()
        } else {
          this.transformNodesFlag = false
        }
      })
      .catch(error => {
        console.log(error)
      })
  },
  returnResults () {
    const path = `http://127.0.0.1:5000/data/sendResults`

    const axiosConfig = {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
        'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS'
      }
    }
    axios.get(path, axiosConfig)
      .then(response => {
        console.log('Server successfully send the predictive results!')
        this.ValidResults = response.data.ValidResults
        EventBus.$emit('finalResults', this.ValidResults)
        if (!this.spaceChange) {
          EventBus.$emit('HistoryCalled', true)
        }
        this.spaceChange = false
        if (this.transformNodesFlag) {
          EventBus.$emit('Default')
        }
      })
      .catch(error => {
        console.log(error)
      })
  },
    ManipulFeature () {
    const path = `http://127.0.0.1:5000/data/AddRemFun`
    const postData = {
      featureAddRem: this.featureAddRem,
    }
    const axiosConfig = { 
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
        'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS'
      }
    }
    axios.post(path, postData, axiosConfig)
      .then(response => {
        console.log('Sent an order to add or remove features!')
        this.threshold()
      })
      .catch(error => {
        console.log(error)
      })
  },
  ManipulFeatureGen () {
    const path = `http://127.0.0.1:5000/data/AddRemGenFun`
    const postData = {
      featureAddRemGen: this.featureAddRemGen,
    }
    const axiosConfig = { 
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
        'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS'
      }
    }
    axios.post(path, postData, axiosConfig)
      .then(response => {
        console.log('Sent an order to add or remove features!')
        this.threshold()
      })
      .catch(error => {
        console.log(error)
      })
  },
  storeGenFun () {
    const path = `http://127.0.0.1:5000/data/storeGeneratedFeatures`
    const postData = {
    }
    const axiosConfig = { 
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
        'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS'
      }
    }
    axios.post(path, postData, axiosConfig)
      .then(response => {
        console.log('Store newly generated features!')
        this.transformNodesFlag = true
        EventBus.$emit('updateHistoryKey', 5)
        this.threshold()
        if (!this.spaceChange) {
          EventBus.$emit('Default')
        }
      })
      .catch(error => {
        console.log(error)
      })
  },
  Compare () {
    const path = `http://127.0.0.1:5000/data/compareFun`
    const postData = {
      getIDs: this.IDToCompare,
      compareNumber: this.compareNumber
    }
    const axiosConfig = { 
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
        'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS'
      }
    }
    axios.post(path, postData, axiosConfig)
      .then(response => {
        console.log('Sent the features to compare!')
        this.returnImportanceComp()
      })
      .catch(error => {
        console.log(error)
    })
  },
  returnImportanceComp () {
    const path = `http://127.0.0.1:5000/data/sendFeatImpComp`
    
    const axiosConfig = {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
        'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS'
      }
    }
    axios.get(path, axiosConfig)
      .then(response => {
        console.log('Server successfully send the importances for comparison!')
        this.ImportanceCompare = response.data.ImportanceCompare
        this.featureNames = response.data.FeatureNames
        EventBus.$emit('Generation', this.featureNames)
        EventBus.$emit('HeatmapCall', this.ImportanceCompare)
      })
      .catch(error => {
        console.log(error)
      })
  },
  transformNodesFun () {
    const path = `http://127.0.0.1:5000/data/transformation`
    const postData = {
      nameClicked: this.storeDataTransf,
      removeNode: this.storeDataTransf
    }
    const axiosConfig = { 
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
        'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS'
      }
    }
    axios.post(path, postData, axiosConfig)
      .then(response => {
        console.log('Features transformation active!')
        this.threshold()
        this.transformNodesFlag = true
      })
      .catch(error => {
        console.log(error)
    })
  }
  },
  created () {

    // does the browser support the Navigation Timing API?
    if (window.performance) {
        console.info("window.performance is supported");
    }
    // do something based on the navigation type...
    if(performance.navigation.type === 1) {
        console.info("TYPE_RELOAD");
        this.Reset();
    }
    window.addEventListener('resize', this.change)
  },
  mounted() {
 var coll = document.getElementsByClassName("collapsible");
    var i;
    var flagLocalMounted = true
    var flagLocalSkip = true
    EventBus.$on('OpenModal', data =>{ flagLocalSkip = false }) 
    for (i = 0; i < coll.length; i++) {
      coll[i].addEventListener("click", function() {
        if (flagLocalSkip) {
          var content = document.getElementsByClassName("content")
          var value = "370px"
          for (let j = 0; j < content.length; j++) {
            if (content[j].style.display === "block") {
              content[j].style.display = "none";
            } else {
              content[j].style.display = "block";
              if (flagLocalMounted) {
                content[j].style.display = "none";
              }
            }
          }
          flagLocalMounted = false
          var combineWH = []
          combineWH.push(this.width)
          combineWH.push(this.height - 100)
        }
      flagLocalSkip = true
      });
    }

    var modal = document.getElementById('myModal')
    window.onclick = function(event) {
      //alert(event.target)
        if (event.target == modal) {
            modal.style.display = "none";
        } 
    }
    this.render(true)
    loadProgressBar()
    window.onbeforeunload = function(e) {
      return 'Dialog text here.'
    }
    $(window).on("unload", function(e) {
      alert('Handler for .unload() called.');
    })

    EventBus.$on('CompareTwo', data => { this.IDToCompare = data })
    EventBus.$on('CompareTwo', data => { this.compareNumber = 1 })
    EventBus.$on('CompareTwo', this.Compare)

    EventBus.$on('CompareThree', data => { this.IDToCompare = data })
    EventBus.$on('CompareThree', data => { this.compareNumber = 2 })
    EventBus.$on('CompareThree', this.Compare)

    EventBus.$on('diactiveTransform', data => { this.transformNodesFlag = true })
    EventBus.$on('activeTransform', data => { this.transformNodesFlag = false })
    EventBus.$on('Default', this.returnImportance)
    EventBus.$on('updateFeatureImp', this.returnCorrel)

    EventBus.$on('ReturningBrushedPointsIDs',  data => { this.modelsUpdate = data })
    //EventBus.$on('ReturningBrushedPointsIDs',  this.UpdateBarChartFeatures )

    EventBus.$on('ConfirmDataSet', data => { this.initAuto = false })
    EventBus.$on('ConfirmDataSet', this.threshold)
    
    EventBus.$on('reset', this.Reset)
    EventBus.$on('ReturningAlgorithms', data => { this.selectedAlgorithms = data })
    EventBus.$on('ReturningBrushedPointsParams', data => { this.parametersofModels = data; })

    EventBus.$on('RemainingPoints', data => { this.unselectedRemainingPoints = data })
    EventBus.$on('InitializeCrossoverMutation', this.sendPointsCrossMutat)

    EventBus.$on('ChangeKey', data => { this.keyNow = data })
    EventBus.$on('sendToServerSelectedScatter', this.SendSelectedPointsToServer)

    EventBus.$on('SendSelectedDataPointsToServerEvent', data => { this.DataPointsSel = data })
    EventBus.$on('SendSelectedDataPointsToServerEvent', this.SendSelectedDataPointsToServer)
    EventBus.$on('SendSelectedFeaturesEvent', data => { this.SelectedFeaturesPerClassifier = data })
    EventBus.$on('sendToServerFeatures', this.UpdateBasedonFeatures)

    EventBus.$on('SendToServerDataSetConfirmation', data => { this.RetrieveValueFile = data })
    EventBus.$on('SendToServerDataSetConfirmation', this.fileNameSend)

    EventBus.$on('SendToServerLocalFile', data => { this.localFile = data })
    EventBus.$on('SendToServerLocalFile', this.SendToServerData)
    EventBus.$on('PCPCall', data => { this.selectedAlgorithm = data })
    EventBus.$on('PCPCall', this.CallPCP)
    EventBus.$on('PCPCallDB', this.SendBrushedParameters)
    EventBus.$on('UpdateBoxPlot', data => { this.brushedBoxPlotUpdate = data })
    EventBus.$on('UpdateBoxPlot', this.UpdateBrushBoxPlot)
    EventBus.$on('CallFactorsView', data => { this.basicValuesFact = data })
    EventBus.$on('CallFactorsView', this.factors)
    EventBus.$on('AllAlModels', data => {
      this.valueSel = data
      this.valueAll = data
    })
    EventBus.$on('sendPointsNumber', data => {this.OverSelLength = data})
    EventBus.$on('sendPointsNumber', data => {this.OverAllLength = data})
    EventBus.$on('sendPointsNumberCM', data => {this.OverSelLengthCM = data})
    EventBus.$on('sendPointsNumberCM', data => {this.OverAllLengthCM = data})
  
    EventBus.$on('AllSelModels', data => {this.valueSel = data})

    EventBus.$on('SendtheChangeinRangePos', data => {this.PositiveValue = data})
    EventBus.$on('SendtheChangeinRangeNeg', data => {this.NegativeValue = data})
    EventBus.$on('SendtheChangeinRangePos', this.threshold)
    EventBus.$on('SendtheChangeinRangeNeg', this.threshold)

    EventBus.$on('addFeature', data => { this.featureAddRem = data })
    EventBus.$on('removeFeatures', data => { this.featureAddRem = data })
    EventBus.$on('addFeature', this.ManipulFeature)
    EventBus.$on('removeFeatures', this.ManipulFeature)

    EventBus.$on('removeFeaturesGen', data => { this.featureAddRemGen = data })
    EventBus.$on('removeFeaturesGen', this.ManipulFeatureGen)
    EventBus.$on('addFeatureGen', data => { this.featureAddRemGen = data })
    EventBus.$on('addFeatureGen', this.ManipulFeatureGen)

    EventBus.$on('transformNodes', data => { this.storeDataTransf = data })
    EventBus.$on('transformNodes', this.transformNodesFun)

    EventBus.$on('flagSpace', data => { this.spaceChange = data })

    EventBus.$on('finalResults', this.openModalCalculate)
    EventBus.$on('OpenModal', this.openModalFun)

    EventBus.$on('storeGeneration', this.storeGenFun)

    //Prevent double click to search for a word. 
    document.addEventListener('mousedown', function (event) {
      if (event.detail > 1) {
      event.preventDefault();
      }
    }, false);
    
  },
})
</script>

<style lang="scss">

#nprogress .bar {
background: red !important;
}

#nprogress .peg {
box-shadow: 0 0 10px red, 0 0 5px red !important;
}

#nprogress .spinner-icon {
border-top-color: red !important;
border-left-color: red !important;
}

body {
  font-family: 'Helvetica', 'Arial', sans-serif !important;
  left: 0px;
  right: 0px;
  top: 0px;
  bottom: 0px;
  margin-top: -4px !important;
  //overflow: hidden !important; // remove scrolling
}

.modal-backdrop {
  z-index: -1 !important;
}

.card-body {
   padding: 0.60rem !important;
}

hr {
  margin-top: 1rem;
  margin-bottom: 1rem;
  border: 0;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

@import './../assets/w3.css';
</style>