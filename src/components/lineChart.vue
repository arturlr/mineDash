<template>
    <vue-frappe
            :id="this.title"
            :labels="this.label"
            :title="this.title"
            :type="this.type"
            :height="150"
            :colors="['purple', '#ffa3ef', 'light-blue']"
            :dataSets="this.dataSet">
        </vue-frappe>
</template>
<script>
    export default {
      name: 'chart',
      props: {
        title: {
          type: String,
          default: 'Title'
        },
        dataChart: {
          type: Object,
          default: () => ({})
        },
        type: {
          type: String,
          default: 'line'
        },
        labels: {
          type: Array,
          default: null
        }
      }
    }
</script>

<script>
import { VueFrappe } from 'vue2-frappe'

export default {
  name: "Chart",
  data() {
    return {      
      dataSet: null
    }
  },
  components: {
    VueFrappe,
  },
  mounted() {
    this.dataSet = this.dataChart
    console.log(this.data)
    console.log(this.labels)
  }
};
</script>

