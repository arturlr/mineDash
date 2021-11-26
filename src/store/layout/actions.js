export function saveLayout({ commit },
    { name }) {
      console.group("store/layout/actions/saveLayout");
      commit("SET_LAYOUT", name);
    }