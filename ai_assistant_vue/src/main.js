import './assets/main.css'
import router from './router';
import App from './App.vue'; 
import store from './store.js'; 
import { createApp } from 'vue'


const app = createApp(App);
app.use(router); // 使用 router
app.use(store); 
app.mount('#app');
// import Login from './Login.vue'
// import axios from './axios.vue'

// createApp(Login).mount('#login')
// createApp(axios).mount('#axios')
