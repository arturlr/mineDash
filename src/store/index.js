import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

import profile from "./profile";
import layout from "./layout";

Vue.use(Vuex);

const modules = {
  profile,
  layout
};

const store = new Vuex.Store({ modules });

export default store;
