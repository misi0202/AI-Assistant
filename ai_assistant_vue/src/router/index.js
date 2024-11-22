import { createRouter, createWebHistory } from 'vue-router';
import Login from '../Login.vue'; 
import Chat from '../Chat.vue';   
import CreateKG from '../CreateKG.vue';
import Uploadfile from '../Upload.vue';
import ModifyKG from '../ModifyKG.vue';
import Choose from '../ChooseCourse.vue';
import User_manage from '../User_manage.vue';
const routes = [
  {
    path: '/',
    name: 'Login',
    component: Login
  },
  {
    path: '/chat',
    name: 'Chat',
    component: Chat
  },
  {
    path: '/createKG',
    name: 'CreateKG',
    component: CreateKG
  }
  ,
  {
    path: '/upload',
    name: 'Uploadfile',
    component: Uploadfile
  }
  ,
  {
    path: '/modify',
    name: 'ModifyKG',
    component: ModifyKG
  },
  {
    path: '/Choose',
    name: 'Choose',
    component: Choose
  },
  {
    path: '/User_manage',
    name: 'user_manage',
    component: User_manage
  }
  
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
