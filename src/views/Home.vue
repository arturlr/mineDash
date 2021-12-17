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
              
              :hint="state"
              persistent-hint
              >
              <v-icon
                slot="prepend"
                @click="startServer"
                v-bind:color="state==='stopped' ? 'error' : state === 'running' && instanceStatus === 'ok' ? 'success' : 'warning'"
              >
              mdi-power
              </v-icon>
              </v-text-field>

              <v-card-text>
                <v-chip
                  class="mr-2"
                  outlined
                >
                  <v-icon left               
                :color="classColor(instanceStatus)"
              >
                mdi-dots-horizontal-circle
              </v-icon> 
                  Instance Status
                </v-chip>
                <v-chip 
                  outlined
                >
                  <v-icon left              
                :color="classColor(systemStatus)"
              >
                mdi-dots-horizontal-circle
              </v-icon>
                  System Status
                </v-chip>
              </v-card-text>

            </v-col>

             <v-col
          cols="12"
          md="3"
        >

         <v-text-field
              label="Instance Type"
              :value="instanceType"
              outlined
              readonly
              >
         </v-text-field>

          </v-col>

          <v-col
          cols="12"
          md="3"
        >

         <v-text-field
              label="Monthly Usage to Date"
              :value="cost.usageQuantity"
              suffix="Hours"
              outlined
              readonly
              >
         </v-text-field>

          </v-col>

         <v-col
          cols="12"
          md="3"
        >

         <v-text-field
              label="Monthly Cost to Date"
              :value="cost.unblendedCost"
              prefix="$"
              outlined
              readonly
              >
         </v-text-field>

          </v-col>
           </v-row>

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

          <v-list>
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
import { mapGetters } from "vuex";

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
    let actionMsg = null
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
        actionMsg = "load page"

      }).catch( function (error) {
        if (error.response) {
          vm.errorAlert = true;
          vm.errorMsg = error.response.data.msg
          actionMsg = error.response.data.msg
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
      actionMsg = error
      console.error(error)
    }

    await this.writeLog(actionMsg)
  
  },
  computed: {
    ...mapGetters({
      isAuthenticated: "profile/isAuthenticated",
      email: "profile/email"
    }),
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
    async writeLog(msg) {
      // Calculating expiration time
      const d = new Date();
      d.setDate(d.getDate() + 60);
      const expirationEpoch = Math.round(d.getTime() / 1000)

      await this.$store.dispatch("profile/saveAuditLogin", {
        email: this.email,
        action: msg,
        expirationEpoch: expirationEpoch
      });
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
      //let actionMsg = null
      if (this.state !== "stopped") {
        this.errorAlert = false;
        this.errorMsg = "Server has to be stopped to be started";
        return false 
      }
      console.log("oi")
      // try {
      //   const currentSession = await Auth.currentSession();
      //   const jwt = currentSession.getAccessToken().getJwtToken();
      //   const options = {
      //     headers: {
      //       'Content-Type': 'application/json;charset=utf-8',
      //       'Authorization': jwt          
      //       }
      //   };

      //   let vm = this;
      //   await this.$http.post(this.baseUrl + "start", 
      //       { instanceId: this.instanceName }, options).then(() => {
      //       this.state = "pending";
      //       this.successAlert = true;
      //       actionMsg = this.instanceName + " started";
      //   }).catch( function (error) {
      //   if (error.response) {
      //     vm.errorAlert = true;
      //     vm.errorMsg = error.response.data.msg
      //     actionMsg = error.response.data.msg;
      //   } else if (error.request) {
      //     // The request was made but no response was received
      //     // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
      //     // http.ClientRequest in node.js
      //     actionMsg = error.request;
      //     console.error(error.request);
      //   } else {
      //     // Something happened in setting up the request that triggered an Error
      //     actionMsg = error.message;
      //     console.error('Error', error.message);
      //   }
      // });
      // } catch (error) {
      //   this.errorAlert = false;
      //   this.errorMsg = error;
      //   console.error(error);
      // }

      // await this.writeLog(actionMsg)

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
