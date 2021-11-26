<template>
  <div>
    <v-app-bar color="black" dense dark fixed app>
      <v-toolbar-title>MineDash</v-toolbar-title>
      <v-spacer></v-spacer>
      <span class="yellow--text">{{ email }}</span>
      <v-tooltip bottom>
      <template v-slot:activator="{ on, attrs }">
        <v-btn 
          icon 
          color="yellow" 
          @click="signOut"
          v-bind="attrs"
          v-on="on"
        >
        <v-icon>mdi-export</v-icon>
      </v-btn>
      </template>
      <span>Sing Out</span>
    </v-tooltip>

      
    </v-app-bar>
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
