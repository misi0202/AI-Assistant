<template>
<div style="visibility: visible; color: #000000;">
  <ul>
    <form style="margin: 20px;">
      <li v-for="([key, user]) in userEntries" :key="key" style="margin: 30px; padding: 30px; border: 1px solid #ccc; height:100px">
        <label for="user_id" style="margin-left:20px;">用户id:</label>
        <input type="text" id="user_id" name="user_id" v-model="user.id" readonly>

        <label for="username" style="margin-left:20px;">用户名:</label>
        <input type="text" id="username" name="username" v-model="user.username">

        <label for="password" style="margin-left:20px;">用户密码:</label>
        <input type="text" id="password" name="password" v-model="user.password">

          <span style="margin-left:20px;">用户权限:</span>
          <input type="radio" :name="'role-' + key" id="role_admin" v-model="user.role" :value="2">
          <label for="role_admin">学生</label>

          <input type="radio" :name="'role-' + key" id="role_teacher" v-model="user.role" :value="1">
          <label for="role_teacher">教师</label>

          <input type="radio" :name="'role-' + key" id="role_student" v-model="user.role" :value="0">
          <label for="role_student">管理员</label>

        <button type="button" @click="updateUser(key, user)">点击修改</button>
      </li>
    </form>
  </ul>
</div>




    
  </template>
  
  
  
  <script setup>
  import { ref, nextTick, onActivated, onMounted, reactive,  computed } from 'vue';
  import { List, Avatar, ButtonGroup, Toast, Button, Notification } from '@kousum/semi-ui-vue';
  import axios from 'axios';
  import { useRouter } from 'vue-router';
  const router = useRouter();
  
  
  const state = reactive({
    UserData: []
  });
  
  const uploadFlag = ref(false);
  const userEntries = computed(() => {
  return Object.entries(state.UserData);
});
  onMounted(async() => {
    console.log('onMounted');
    await getUserlist(); // 页面首次加载时获取数据
    console.log(state.UserData);
  });
  
  onActivated(async() => {
    console.log('onActivated');
    await getUserlist(); // 页面重新激活时重新获取数据
    console.log(state.UserData);
  });
  
  async function getUserlist() {
    try {
      const res = await axios.get('http://127.0.0.1:5000/api/user_list');
      state.UserData = res.data;
      console.log(state.UserData);
      nextTick(() => {
        console.log('nextTick');
      });
    } catch (err) {
      Toast.error('获取用户失败');
    }
  }
  

  
  async function updateUser(key, user) {
    console.log('更新用户:', user);
    const username = user.username;
    const password = user.password;
    const id = user.id;
    const role = user.role;
    try {

      const res = await axios.post('http://127.0.0.1:5000/api/UpdateUser',{
        user_id: id,
        username: username,
        password: password,
        role: role
      });
      state.UserData = res.data;
      console.log(state.UserData);
      nextTick(() => {
        Toast.success('用户更新成功');
      });
    } catch (err) {
      Toast.error('用户更新失败');
    }
    router.push({ name: 'Choose' });
  }
  </script>
  
  <style scoped>

  </style>
  