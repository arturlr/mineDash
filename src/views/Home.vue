<template>
  <div>
    <v-alert type="info" v-model="successAlert" dismissible>
      Starting Instace. Please refresh this page in one/two minutes.
    </v-alert>
    <v-alert type="error" v-model="errorAlert" dismissible>
      {{ errorMsg }}
    </v-alert>

<v-container fluid>
   <v-row>
     <v-col cols="4">
      
      <v-card class="pa-2">
        <v-list-item>
          <v-list-item-content>
            <div class="text-overline mb-4">
              HOSTNAME
            </div>
          </v-list-item-content>
        </v-list-item>
        <v-spacer></v-spacer>
        <v-row>
            <v-col cols="12">
               <v-text-field
              id="publicIp"
              dense
              label="Public IP"
              :value="publicIp"
              append-icon="content_copy"
              @click:append="copyPublicIp"
              :hint="state"
              persistent-hint
              outlined
              readonly
              >
               <v-icon
                large
                slot="prepend"
                @click="startServer"
                v-bind:color="state==='stopped' ? 'error' : state === 'running' && instanceStatus === 'ok' ? 'success' : 'warning'"
              >
              mdi-power
              </v-icon>
              <template v-slot:append-outer>
                  <v-progress-circular
                    v-if="state === 'running' && instanceStatus !== 'ok' && systemStatus !='ok'"
                    size="24"
                    color="info"
                    indeterminate
                  ></v-progress-circular>
              </template>
              </v-text-field>  

              <v-chip
                class="ma-2"
                color="gray"
                label
                outlined
              >
                <v-icon left>             
                  developer_board
                </v-icon>
                2 vCPU
              </v-chip>

              <v-chip
                class="ma-2"
                color="gray"
                label
                outlined
              >
                <v-icon left>             
                  sd_card
                </v-icon>
                4 GB
              </v-chip>

              <v-chip
                class="ma-2"
                color="gray"
                label
                outlined
              >
                <v-icon left>             
                  album
                </v-icon>
                50 GB
              </v-chip>  

              <v-divider></v-divider>          
  
              <v-chip
                class="ma-2"
                color="primary"
                label
                outlined
              >
                <v-icon left>             
                  attach_money
                </v-icon>
                {{ cost.unblendedCost }}
              </v-chip>

              <v-chip
                class="ma-2"
                color="primary"
                label
                outlined
              >
              <v-icon left>
                  schedule
                </v-icon>
                {{ cost.usageQuantity }} hours
              </v-chip>

              <v-chip
                class="ma-2"
                color="primary"
                label
                outlined
              >
              <v-icon left>
                  group
                </v-icon>
                0
              </v-chip>
             
            </v-col>
        </v-row>

        <v-row>
            <v-col cols="12">
              <v-card>
              <v-list class="transparent">
                
                <v-list-item two-line>
                  <v-list-item-content>
                    <v-list-item-title class="text-h7 font-weight-light">
                      CPU - Last 4 hours
                    </v-list-item-title>
                    <v-list-item-subtitle>
                      <apexchart ref="cpuUtilization" height="45" 
                          :options="sparklineOptions" :series="chartInit"></apexchart>
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>

                <v-list-item two-line>
                  <v-list-item-content>
                    <v-list-item-title class="text-h7 font-weight-light">
                      Network - Last 4 hours
                    </v-list-item-title>
                    <v-list-item-subtitle>
                      <apexchart ref="networkOut"  height="45" 
                          :options="sparklineOptions" :series="chartInit"></apexchart>
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>

                <v-list-item two-line>
                  <v-list-item-content>
                    <v-list-item-title class="text-h7 font-weight-light">
                      Last 15 days usage (min)
                    </v-list-item-title>
                    <v-list-item-subtitle>
                      <apexchart ref="usage"  height="45" 
                          :options="barOptions" :series="chartInit"></apexchart>
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-list>

              </v-card>

            </v-col>

           </v-row>

          <v-list>
          <v-list-item two-line>
            <v-list-item-content>
            <v-list-item-title class="font-weight-light">
              Last launch time
            </v-list-item-title>
            <v-list-item-subtitle class="font-weight-light">{{ launchTime }}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-list>

      </v-card>
     </v-col>
    </v-row>

</v-container>

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
import { Auth } from "aws-amplify";
import { mapGetters } from "vuex";
import VueApexCharts from "vue-apexcharts";
//import moment from "moment";

export default {
  name: "App",
  components: {
    apexchart: VueApexCharts,
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
      statusCode: 200,
      errorAlert: false,
      errorMsg: null,
      successAlert: false,
      copyDialog: false,
      sparklineOptions: {
        chart: {
          type: 'line',
          sparkline: {
            enabled: true
          }
        },
        tooltip: {
          fixed: {
            enabled: false
          },
          x: {
            show: false
          },
          y: {
            
          },
          marker: {
            show: false
          }
        }
      },
      barOptions: {
        chart: {
          type: 'bar',
          sparkline: {
            enabled: true
          }
        },
        plotOptions: {
          bar: {
            columnWidth: '80%'
          }
        },
        labels: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,12,14,15],
        xaxis: {
          crosshairs: {
            width: 1
          },
        },
        tooltip: {
          fixed: {
            enabled: false
          },
          x: {
            show: false
          },
          y: {
            
          },
          marker: {
            show: false
          }
        }

      },
      chartInit: [{
        data: []
      }],
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
        this.getChartData("networkOut");
        this.getChartData("cpuUtilization");        
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
        this.getChartData("networkOut");
        this.getChartData("cpuUtilization");
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
      let actionMsg = null
      if (this.state !== "stopped") {
        this.errorAlert = false;
        this.errorMsg = "Server has to be stopped to be started";
        return false 
      }
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
            { instanceId: this.instanceName }, options).then(() => {
            this.state = "pending";
            this.successAlert = true;
            actionMsg = this.instanceName + " started";
        }).catch( function (error) {
        if (error.response) {
          vm.errorAlert = true;
          vm.errorMsg = error.response.data.msg
          actionMsg = error.response.data.msg;
        } else if (error.request) {
          // The request was made but no response was received
          // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
          // http.ClientRequest in node.js
          actionMsg = error.request;
          console.error(error.request);
        } else {
          // Something happened in setting up the request that triggered an Error
          actionMsg = error.message;
          console.error('Error', error.message);
        }
      });
      } catch (error) {
        this.errorAlert = false;
        this.errorMsg = error;
        console.error(error);
      }

      await this.writeLog(actionMsg)

    },
    getChartData(metricName) {
      
      if (this.metrics[metricName] && this.metrics[metricName].length != 0) {
          this.$refs.metricName.updateSeries([
          {
            name: metricName,
            data: this.metrics[metricName]
          }
        ])
      }
    } // function 
  } // methods
};
</script>