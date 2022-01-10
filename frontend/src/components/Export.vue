<template>
  <div id="ExportResults">
  =======================================================
  <br>
  New features: {{ FeaturesPickled }}
  <br>
  =======================================================
  </div>
</template>

<script>

import { EventBus } from '../main.js'
import * as Cryo from 'cryo'
export default {
  name: 'Export',
  data () {
    return {
      FeaturesPickled: '',
      Features: [],
    }
  },
  methods: {
    Pickle () {
      this.FeaturesPickled = Cryo.stringify(this.Features)
    }
  },
  mounted () {
    EventBus.$on('sendSelectedFeaturestoPickle', data => {
    this.Features = data})
    EventBus.$on('sendSelectedFeaturestoPickle', this.Pickle)
  }
}
</script>

<style scoped>
#ExportResults {
  word-break: break-all !important;
}
</style>