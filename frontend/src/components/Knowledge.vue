<template>
  <h5><button class="btn-outline-custom"
  style="float: center;"
  id="know"
  v-on:click="knowClass">
  <font-awesome-icon icon="file-export" />
  {{ valueKnowE }}
  </button></h5>
</template>

<script>

import { EventBus } from '../main.js'

export default {
  name: 'Knowledge',
  data () {
    return {
      valueKnowE: 'Feature extraction'
    }
  },
  methods: {
      knowClass () {
        EventBus.$emit('OpenModal')
      }
  }
}
</script>

<style>

.btn-outline-custom {
    color: #B15928;
    background-color: #FFFFFF;
    border-color: #B15928;
}

.btn-outline-custom:hover {
    color: #FFFFFF;
    background-color: #B15928;
    border-color: #B15928;
}

</style>