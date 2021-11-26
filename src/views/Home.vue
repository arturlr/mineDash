<template>
  <div>
    <v-alert type="info" v-model="successAlert" dismissible>
      Starting Instace. Please refresh this page in one/two minutes.
    </v-alert>
    <v-alert type="error" v-model="errorAlert" dismissible>
      {{ errorMsg }}
    </v-alert>
    <v-row class="ma-5">
      <v-card class="pa-2">
        <v-card-text>
          <p class="text-h5 text--primary">
            Server Start/Stop Events
          </p>
          <v-virtual-scroll :items="items" :item-height="90" height="400">
            <template v-slot:default="{ item }">
              <v-timeline align-top dense>
                <v-timeline-item v-if="item.type === 'stop'" color="red" small>
                      <span class="text-caption"> {{ item.dt }}</span>
                      <strong>
                        {{ item.user }}
                      </strong>
                </v-timeline-item>
                <v-timeline-item v-if="item.type === 'start'" color="green" small>
                      <span class="text-caption"> {{ item.dt }}</span>
                      <strong>
                        {{ item.user }}
                      </strong>
                </v-timeline-item>
              </v-timeline>
            </template>
          </v-virtual-scroll>
        </v-card-text>
      </v-card>
      <v-card class="pa-2">
           <v-row>
            <v-col cols="12">
              <v-text-field
              id="publicIp"
              label="Public IP"
              :value="publicIp"
              prepend-icon="content_copy"
              @click:prepend="copyPublicIp"
              outlined
              readonly
              ></v-text-field>

              <v-text-field
              label="Instance Id"
              dense
              :value="instanceName"
              outlined
              readonly
              ></v-text-field>

              <v-text-field
              label="Instance Type"
              dense
              :value="instanceType"
              outlined
              readonly
              ></v-text-field>

              <v-btn
                v-if="state === 'stopped'"
                title
                medium
                color="error"
                ><v-icon left>
                  mdi-power
                </v-icon>
                stopped
              </v-btn>
              <v-btn
                v-if="state === 'running' && instanceStatus != 'ok'"
                title
                medium
                color="warning"
                ><v-icon left>
                  mdi-power
                </v-icon>
                LOADING
              </v-btn>
              <v-btn
                v-if="state === 'running' && instanceStatus === 'ok'"
                title
                medium
                color="success"
                ><v-icon left>
                  mdi-power
                </v-icon>
                running
              </v-btn>
                <v-btn
                  v-if="state === 'stopped'"
                  class="p-8"
                  title
                  medium                  
                  @click="startServer"
                ><v-icon left >restart_alt</v-icon>
                Start
                </v-btn>

            </v-col>
           </v-row>

          <v-list>
          <v-list-item two-line>
            <v-list-item-content>
            <v-list-item-title class="text-bold">
              Instance Status
            </v-list-item-title>
            <v-list-item-subtitle>
              <v-icon                
                :color="classColor(instanceStatus)"
              >
                mdi-dots-horizontal-circle
              </v-icon> 
            </v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>

          <v-list-item two-line>
            <v-list-item-content>
            <v-list-item-title class="text-bold">
              System Status
            </v-list-item-title>
            <v-list-item-subtitle>
              <v-icon                
                :color="classColor(systemStatus)"
              >
                mdi-dots-horizontal-circle
              </v-icon>             
            </v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>

          <v-list-item two-line>
            <v-list-item-content>
            <v-list-item-title class="text-bold">
              Last launch time
            </v-list-item-title>
            <v-list-item-subtitle>{{ launchTime }}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-card>
      <v-card class="pa-2" width="350">
          <v-card-text>
            <div>MONTHLY USAGE TO DATE</div>
            <p class="text-h4 text--primary">
              {{ cost.usageQuantity }} hours
            </p>
            <p>MONTHLY COST TO DATE</p>
            <p class="text-h4 text--primary">
              $ {{ cost.unblendedCost }}
            </p>
          </v-card-text>
          <v-card height="150">
          <vue-frappe v-if="state === 'running' && cpuChartData != null"
            id="cpu"
            :key="timeEpoch"
            type="line"
            :height="150"
            :lineOptions="{regionFill: 1}"
            :dataSets="cpuChartData.data"
            :labels="cpuChartData.labels"
            title="CPU Utilization"
          />
          </v-card>
          <v-divider></v-divider>
          <v-card height="150">
          <vue-frappe v-if="state === 'running' && networkOutChartData != null"
            id="network"
            :key="timeEpoch"
            type="line"
            :height="150"
            :lineOptions="{regionFill: 1}"
            :dataSets="networkOutChartData.data"
            :labels="networkOutChartData.labels"
            title="Network Out"
          />
          </v-card>
      </v-card>
    </v-row>
    <v-dialog
      v-model="copyDialog"
      hide-overlay
      persistent
      width="300"
    >
      <v-card
        color="primary"
        dark
      >
        <v-card-text>
          Copied IP Address to Clipboard
          <v-progress-linear
            color="white"
            class="mb-0"
          ></v-progress-linear>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="green darken-1"
            text
            @click="copyDialog = false"
          >
            Ok
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { VueFrappe } from 'vue2-frappe'
import { Auth } from "aws-amplify";

export default {
  name: "App",
  components: {
    VueFrappe,
  },
  data() {
    return {
      baseUrl: process.env.VUE_APP_APIURL,
      instanceName: null,
      instanceType: null,
      state: null,
      launchTime: null,
      publicIp: null,
      instanceStatus: null,
      systemStatus: null,
      cost: {
        usageQuantity: 0, 
        unblendedCost: 0 
      },
      timeEpoch: null,
      items: [],
      timeStamp: null,
      cpuChartData: null,
      networkOutChartData: null,
      statusCode: 200,
      errorAlert: false,
      errorMsg: null,
      successAlert: false,
      copyDialog: false
    };
  },

  async mounted() {
    try {      
      const currentSession = await Auth.currentSession();
      const jwt = currentSession.getAccessToken().getJwtToken();
    
      const options = {
        headers: {
          'Content-Type': 'application/json;charset=utf-8',
          'Authorization': jwt        }
      };

      let vm = this;
      await this.$http.post(this.baseUrl + "info", {} ,options).then((result) => {
        this.instanceName = result.data.instanceName;
        this.instanceType = result.data.instanceType;
        this.state = result.data.state;
        this.launchTime = result.data.launchTime;
        this.publicIp = result.data.publicIp;
        this.instanceStatus = result.data.instanceStatus;
        this.systemStatus = result.data.systemStatus;
        this.timeLine = result.data.timeLine;
        this.metrics = result.data.metrics;
        this.cost = result.data.cost;

        // Populating the items array for timeline
        this.timeLine.forEach((element) => {
        let rec = element.split("#");
        let user = null;
        if (rec[1].length > 16) {
          user = rec[1].substr(0, 16);
        } else {
          user = rec[1];
        }
        if (rec[2] == "StartInstances") {
          this.items.push({ type: "start", dt: rec[0], user: user });
        } else if (rec[2] == "StopInstances") {
          this.items.push({ type: "stop", dt: rec[0], user: user });
        }
        });
        this.timeEpoch = Date.now();
        this.networkOutChartData = this.getChartData("networkOut");
        this.cpuChartData = this.getChartData("cpuUtilization");

      }).catch( function (error) {
        if (error.response) {
          vm.errorAlert = true;
          vm.errorMsg = error.response.data.msg
        } else if (error.request) {
          // The request was made but no response was received
          // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
          // http.ClientRequest in node.js
          console.log(error.request);
        } else {
          // Something happened in setting up the request that triggered an Error
          console.log('Error', error.message);
        }
      });
      
    } catch (error) {
      //this.errorAlert = true;
      //this.errorMsg = error.errorMsg
      console.error(error)
    }
  
  },
  methods: {
    classColor(state) {
      if (state === 'running' || state === "ok") {
        return "green"
      }
      else if (state === 'stopped' || state === 'fail') {
        return "red"
      }
      else {
        return "orange"
      }      
    },
    setShow() {
      setTimeout(() => {
        this.timeEpoch = Date.now();
        this.networkOutChartData = this.getChartData("networkOut");
        this.cpuChartData = this.getChartData("cpuUtilization");
      }, 300.0*1000);
    },
    copyPublicIp () {
          let serverIp = document.querySelector('#publicIp')
          serverIp.setAttribute('type', 'text')
          serverIp.select()
          try {
            document.execCommand('copy');
          } catch (err) {
            console.error('Oops, unable to copy');
          }
          serverIp.setAttribute('type', 'hidden');
          this.copyDialog = true;
    },
    async startServer() {
      try {
        const currentSession = await Auth.currentSession();
        const jwt = currentSession.getAccessToken().getJwtToken();

        const options = {
          headers: {
            'Content-Type': 'application/json;charset=utf-8',
            'Authorization': jwt          
            }
        };

        let vm = this;
        await this.$http.post(this.baseUrl + "start", 
            { instanceId: this.instanceName }, options).then((result) => {
            this.state = "pending";
            this.successAlert = true;
            console.log(result);
        }).catch( function (error) {
        if (error.response) {
          vm.errorAlert = true;
          vm.errorMsg = error.response.data.msg
        } else if (error.request) {
          // The request was made but no response was received
          // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
          // http.ClientRequest in node.js
          console.error(error.request);
        } else {
          // Something happened in setting up the request that triggered an Error
          console.error('Error', error.message);
        }
      });
      } catch (error) {
        this.errorAlert = false;
        this.errorMsg = error;
        console.error(error);
      }
    },
    getChartData(metricName) {
      let labels = [];
      let datasetData = [];

      if (this.metrics[metricName] && this.metrics[metricName].length != 0) {
        this.metrics[metricName].forEach((element) => {
          labels.push(element["label"]);
          datasetData.push(element["value"]);
        });
      }

      return {
          labels: labels,
          data: [{
            values: datasetData 
          }]          
      }
    } // function 
  } // methods
};
</script>
