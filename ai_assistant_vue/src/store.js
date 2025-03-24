import { createStore } from 'vuex';

const store = createStore({
  // 全局状态，所有组件都能访问
  state: {
    chatCourse: 'none',

  },
  
  // mutations 用于同步地更改状态
  mutations: {
    updateMessage(state, newMessage) {
      state.chatCourse = newMessage;
    },
    updateUser(state, user) {
      state.user = user;
    }
  },

  // actions 用于处理异步操作，并提交 mutations 以改变状态
  actions: {
    fetchUserData({ commit }) {
      setTimeout(() => {
        const data = { name: 'Bob', age: 30 };  // 模拟异步数据
        commit('updateUser', data);
      }, 1000);
    }
  },

  // getters 用于获取计算后的状态
  getters: {
    welcomeMessage: (state) => `Welcome, ${state.user.name}!`,
    userAge: (state) => state.user.age
  }
});

export default store;
