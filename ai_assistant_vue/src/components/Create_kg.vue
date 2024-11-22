<template>
  <div>
    <div class="title">创建知识库</div>
  <Form @submit="handleSubmit" :style="{ width: '400px', padding:'20px' }">
    
    <template v-slot="">
 
      <Form.Input 
        field="KGName" 
        label="知识库名称" 
        :style="{ width: '100%', margin: '20px 0px 10px 0px' }" 
        placeholder="请输入知识库名称"
        :rules="[
                    { required: true, message: 'required error' },
                    { type: 'string', message: 'type error' },
                ]"
      ></Form.Input>


      <Form.Checkbox 
        field="agree" 
        :noLabel="true"
        :style="{ width: '100%', margin: '10px 0px 20px 0px' }"
      >
        我阅读并确定相关协议
      </Form.Checkbox>
      <div style="display: flex; justify-content: space-between; align-items: center;">

        <Button 
          htmlType="submit" 
          type="tertiary"
          :style="{ width: '100%', }"
        >
          提交表单
        </Button>
      </div>
    </template>
  </Form>
</div>
</template>

<script setup>
document.body.style.backgroundImage = 'linear-gradient(to bottom, #f0edf7, #e4eaf7)';; 
import { ref } from 'vue';
import { Form, Toast, Button, Col } from '@kousum/semi-ui-vue';
import axios from 'axios';

const handleSubmit = (values) => {
  axios.post('http://127.0.0.1:5000/api/create_knowledge', values)
    .then(res => {
      Toast.success('创建成功');
    })
    .catch(err => {
      Toast.error('创建失败');
    });
};
</script>

<style scoped>
/* Add any custom styles here */
</style>
