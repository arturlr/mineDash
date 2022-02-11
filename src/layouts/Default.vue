<template>
  <div>
    <v-toolbar 
      dark 
      height="100px"
      >
      <v-spacer />
      <v-toolbar-title class="text-h5 font-weight">MineDash</v-toolbar-title>
      <v-spacer />

      <v-menu
      v-model="menu"
      :close-on-content-click="false"
      :nudge-width="200"
      offset-y
    >
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          v-bind="attrs"
          v-on="on"
        >
          <v-icon large>
            assignment_ind
          </v-icon>
        </v-btn>
      </template>

      <v-card dark>
        <v-list>
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title>{{ email }}</v-list-item-title>
            </v-list-item-content>
            <v-list-item-action>
              <v-btn 
                icon 
                color="yellow" 
                @click="signOut"
                v-bind="attrs"
                v-on="on"
              >
              <v-icon>mdi-export</v-icon>
            </v-btn>
            </v-list-item-action>
          </v-list-item>
        </v-list>
      </v-card>
      </v-menu>
    </v-toolbar>


    <v-main>
      <v-container>
        <router-view></router-view>
      </v-container>
    </v-main>
    <v-footer color="black" app>
      <span class="white--text">&copy; Rodrigues</span>
    </v-footer>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { Auth } from "aws-amplify";

export default {
  name: "DefaultLayout",
  data: () => ({
    temp: null,
  }),
  props: {
    source: String,
  },
  methods: {
    async signOut() {
      try {
        await Auth.signOut();
        this.$router.push("/auth");
      } catch (error) {
        console.log("error signing out: ", error);
      }
    },
  },
  computed: {
    ...mapGetters({
      isAuthenticated: "profile/isAuthenticated",
      email: "profile/email"
    }),
  },
};
</script>
