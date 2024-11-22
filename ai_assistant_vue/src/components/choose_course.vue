<template>
    <div class = "cards ">


<CardGroup :spacing="10">
  <Card
    v-for="(item, idx) in Object.entries(state.dataArray)"
    :key="idx"
    shadows="hover"

    :headerLine="false"
    :style="{ width: '300px', padding: '10px', height: '300px' }"
    field="chunkSeqId"
  >
    <Form @submit="KGNameSubmit">
      <!-- 隐藏的输入框以传递数据 -->
      <Form.Input 
        label="" 
        field="CourseName" 
        :style="{ display: 'none', margin: '30px 0px 0px 30px' }" 
        :init-value="item[1]"
      />
      
      <!-- 显示来源信息 -->
      <Typography field="source" :style="{ margin:'50px' }">{{ item[1] }}</Typography>

      <!-- 修改按钮 -->
      <Button htmlType="submit" type="tertiary" :style="{ margin:'50px', width:'150px' }">点击确认</Button>
    </Form>
  </Card>
</CardGroup>
    </div>
      </template>
    
      
      <script setup>
      
      document.body.style.backgroundImage = 'linear-gradient(to bottom, #f0edf7, #e4eaf7)';
      import { ref, nextTick, onActivated, onMounted, reactive } from 'vue';
      import { Form, Toast, Card, CardGroup, Typography, Button, Notification, Modal,  TextArea } from '@kousum/semi-ui-vue';
      import { useStore } from 'vuex';
      import { useRouter } from 'vue-router';
      import axios from 'axios';
    
        const state = reactive({
        dataArray:[]
        });

    
    
      onMounted(() => {
        console.log('onMounted');
        selectKGName(); // 页面首次加载时获取数据
      });
      onActivated(() => {
        console.log('onActivated');
        selectKGName(); // 页面重新激活时重新获取数据
      });
    
      document.addEventListener("DOMContentLoaded", function() {
        selectKGName();
        }
      );

      const getKGname = async () => {
        try {
            const res = await axios.get('http://127.0.0.1:5000/api/get_knowledgename');
            state.dataArray = res.data;
            console.log(state.dataArray);
        } catch (err) {
            Toast.error('获取知识库失败');
        }
      };
      async function selectKGName(){
        await getKGname();
        nextTick(() => {
            console.log('nextTick');
        });
      }


   
    const store = useStore();
    const router = useRouter();
    const KGNameSubmit = (values) => {
      console.log(values.CourseName);
      const newMessage = ref(values.CourseName);
      store.commit('updateMessage', newMessage.value);
      router.push({ name: 'Chat' });
    };
      </script>
      
      <style scoped>
      /* Add any custom styles here */
      .semi-typography{
        margin-top: 50px;
        font-family: "微软雅黑", "黑体", "宋体";
        font-size: 36px;
        margin-left: 30px;
      }
      </style>
      