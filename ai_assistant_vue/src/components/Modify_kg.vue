<template>
<div class = "cards ">
    <Form @submit="KGNameSubmit" :style="{ width: '400px', padding:'20px' }">
    <Form.TreeSelect
            field="KGName"
            :style="{ width: '90%' , visibitily:'hidden'}"
            label='知识库选择'
            placeholder='请选择知识库'
            :tree-data="treeData"
            :rules="[{ required: true, message: 'required error' }]"
            filter-tree-node
          >
    </Form.TreeSelect>
    <Button htmlType="submit" type="tertiary" :style="{ width: '324px', }">
            确定
    </Button>
    </Form>
    <Form @submit="BookSubmit" :style="{ width: '400px', padding:'20px' }">
    <Form.TreeSelect
            field="BookName"
            :style="{ width: '90%' , visibitily:'hidden'}"
            label='文件选择'
            placeholder='请选择知识库内文件'
            :tree-data="BookData"
            :rules="[{ required: true, message: 'required error' }]"
            filter-tree-node
          >
    </Form.TreeSelect>
    <Button htmlType="submit" type="tertiary" :style="{ width: '324px', }">
            确定
    </Button>
    </Form>
  <CardGroup :spacing=10 >
    
    <Card
      v-for="(item, idx) in state.dataArray"
      :key="idx"
      shadows="hover"
      :title="'序号: ' + item.chunkSeqId"
      :headerLine="false"
      :style="{ width: '480px', padding: '10px' , height:'400px'}"
      field="chunkSeqId"
    >
    <Form @submit="ModifyChunk">
      <Form.Input label="————————————————————————————————————————" field="chunkSeqId" :style="{ display: 'none'}" :init-value="item.chunkSeqId"></Form.Input>
      <Form.TextArea label="内容：" :init-value="item.content" field="content"/>
      <Form.Input label="————————————————————————————————————————" field="nothing" :style="{ display: 'none'}" :init-value="item.source"></Form.Input>
      <Typography field="source">来源：{{item.source}}</Typography>
      
      <Form.Input label="————————————————————————————————————————" field="source" :style="{ display: 'none'}" :init-value="item.source"></Form.Input>
      <Button htmlType="submit" type="tertiary" >点击修改</Button>
    </Form> 
    </Card>
  </CardGroup>
</div>
  </template>

  
  <script setup>
  
  document.body.style.backgroundImage = 'linear-gradient(to bottom, #f0edf7, #e4eaf7)';
  import { ref, nextTick, onActivated, onMounted, reactive } from 'vue';
  import { Form, Toast, Card, CardGroup, Typography, Button, Notification, Modal,  TextArea } from '@kousum/semi-ui-vue';
  import axios from 'axios';
import { backtopEmits } from 'element-plus';

  let treeData = [];
  let BookData = [];
  let kg_name = "";
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
        const names = res.data;
        treeData = ref(names.map((name, index) => ({
            label: name,
            value: name,
            key: String(index), // 使用索引作为唯一的 key 值
        })));
    } catch (err) {
        Toast.error('获取知识库失败');
    }
  };
  async function selectKGName(){
    const selectBox = document.getElementsByClassName("semi-form-field-main");
    selectBox[0].style.visibility = 'hidden';
    await getKGname();
    nextTick(() => {
      console.log('TreeSelect 数据已更新:', treeData.value);
      selectBox[0].style.visibility = 'visible';
    });
  }
  const KGNameSubmit = (values) => {
    console.log("知识库选择",values.KGName);
    selectBookName(values.KGName);
    kg_name = values.KGName;
    Notification.info({
        title: '已选择知识库',
        content: '请继续选择书籍',
        duration: 3,
        theme: 'light',
      });
  };
  const getBookname = async (KGName) => {
    try {
        const res = await axios.post('http://127.0.0.1:5000/api/get_books', {KGName:KGName});
        const names = res.data;
        BookData = ref(names.map((name, index) => ({
            label: name,
            value: name,
            key: String(index), // 使用索引作为唯一的 key 值
        })));
    } catch (err) {
        Toast.error('获取知识库失败');
    }
  };
  async function selectBookName(KGName){
    const selectBox = document.getElementsByClassName("semi-form-field-main");
    selectBox[1].style.visibility = 'hidden';
    await getBookname(KGName);
    nextTick(() => {
      console.log('BookSelect 数据已更新:', BookData.value);
      selectBox[1].style.visibility = 'visible';
    });
  }
  const BookSubmit = async (values) => {
  console.log("知识库选择", kg_name);
  console.log("书籍选择", values.BookName);

  Notification.info({
    title: '已选择书籍',
    content: '请选择需要修改的Chunk',
    duration: 3,
    theme: 'light',
  });

  try {
    // 使用 await 等待请求完成
    const res = await axios.post('http://127.0.0.1:5000/api/get_chunks', {
      KGName: kg_name,
      BookName: values.BookName
    });

    state.dataArray = res.data;  // 获取 data 数组
    const element = document.querySelector('.semi-navigation');
    element.style.width = '20000px';
    nextTick(() => {
        Notification.success({
        title: '已获取Chunk',
        content: '',
        duration: 3,
        theme: 'light',
    });
      console.log('Chunk 数据已更新:', state.dataArray);
    });


    
  } catch (err) {
    console.error('Error:', err);
    Toast.error('获取Chunk失败');
  }
};

const ModifyChunk = (values) => {
  console.log(values.chunkSeqId);
  console.log(values.content);
  console.log(values.source);
  // 处理按钮点击逻辑
  axios.post('http://127.0.0.1:5000/api/modify_chunk', {
    BookName: values.source,
    chunkSeqId: values.chunkSeqId,
    content: values.content
  })

  .then(res => {
    console.log(res.data);
    location.reload();
    Notification.success({
      title: '修改成功',
      content: '',
      duration: 3,
      theme: 'light',
    });
  })
};
  </script>
  
  <style scoped>
  /* Add any custom styles here */

  </style>
  