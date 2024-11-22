<script setup>
import { ref } from 'vue';
import axios from 'axios';

// 定义方法
const test = () => {
const data = {
  "1231": "123"
};

axios.post('http://127.0.0.1:5000/api/test', data)
  .then(res => {
    // console 里面打印后端来的 response 数据
    console.log(res.data);
  })
  .catch(err => {
    console.error('Error:', err);
  });
};
</script>
<template>
  <button @click="test">here</button>
</template>