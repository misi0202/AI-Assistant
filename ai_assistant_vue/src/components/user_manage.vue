<template>
    <div style="visibility: visible; color: #000000;">
      <ul>
        <li v-for="([key, user],) in userEntries" :key="key" style="margin-bottom: 10px; padding: 10px; border: 1px solid #ccc;">
          <p style="display: inline; margin-right: 10px; padding: 5px; border: 1px solid #000;">Username: {{ user.username }}</p>
          <p style="display: inline; margin-right: 10px; padding: 5px; border: 1px solid #000;">Password: {{ user.password }}</p>
          <p style="display: inline; margin-right: 10px; padding: 5px; border: 1px solid #000;">ID: {{ user.id }}</p>
          <Button>点击修改</Button>
        </li>
      </ul>
    </div>
  </template>
  
  
  
  <script setup>
  import { ref, nextTick, onActivated, onMounted, reactive,  computed } from 'vue';
  import { List, Avatar, ButtonGroup, Toast, Button, Notification } from '@kousum/semi-ui-vue';
  import axios from 'axios';
  
  
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
      Toast.error('获取知识库失败');
    }
  }
  
  const handleFileChange = () => {
    uploadFlag.value = true;
    console.log("uploadFlag", uploadFlag.value);
  };
  
  const handleSubmit = (values) => {
    console.log("Form", values.tree);
    if (!uploadFlag.value) {
      Toast.error('请上传文件');
    } else {
      console.log("上传文件");
      Notification.info({
        title: '上传文件至知识库',
        content: '请稍等,上传时不要关闭此页面',
        duration: 0,
        theme: 'light',
      });
      const data = { KGName: values.tree };
      axios.post('http://127.0.0.1:5000/api/upload2kg', data)
        .then(res => {
          console.log(res.data);
          Notification.success({
            title: '上传成功',
            content: '文件已解析至对应知识库',
            duration: 0,
            theme: 'light',
          });
        })
        .catch(err => {
          console.error('Error:', err);
        });
    }
  };
  </script>
  
  <style scoped>
  div.semi-form-field {
    width: 400px;
    font-size: 12px;
    font-weight: bold;
  }
  </style>
  