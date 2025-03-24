<template>
    <div>
        <div class="title">上传文件至知识库</div>

    <Form @submit="handleSubmit" :style="{ width: '400px', padding:'20px' }">
      
      <template v-slot="">
 
          <Form.TreeSelect
            field="tree"
            :style="{ width: '90%' , visibitily:'hidden'}"
            label='知识库选择'
            placeholder='请选择知识库'
            :tree-data="treeData"
            :rules="[{ required: true, message: 'required error' }]"
            filter-tree-node
          >
          </Form.TreeSelect>
          <Upload
        ref="uploadRef"
        action = "http://127.0.0.1:5000/api/upload"
        :style="{ width: '350px', padding:'0px 0px 20px 0px' }"
        draggable=true
        dragMainText="点击上传文件或拖拽文件到这里"
        dragSubText="支持pdf、pptx等格式文件"
        accept=".pdf,.ppt,.pptx"
        :on-change="handleFileChange"
        :rules="[{ required: true, message: 'required error' }]"
        >
      </Upload>

  
          <Button 
            htmlType="submit" 
            type="tertiary"
            :style="{ width: '100%', }"
          >
            确定
          </Button>

      </template>
    </Form>
    <div>


      </div>
</div>
  </template>
  
  <script setup>

  document.body.style.backgroundImage = 'linear-gradient(to bottom, #f0edf7, #e4eaf7)';; 
  import { ref, nextTick, onActivated, onMounted } from 'vue';
  import { Form, Toast, Button, Upload, Notification } from '@kousum/semi-ui-vue';
  import axios from 'axios';


  const selectedFile = ref(null);
  let treeData = [];
  const uploadFlag = ref(false);
  onMounted(() => {
    console.log('onMounted');
  selectFunc(); // 页面首次加载时获取数据
  });
  onActivated(() => {
    console.log('onActivated');
    selectFunc(); // 页面重新激活时重新获取数据
  });

  document.addEventListener("DOMContentLoaded", function() {
    selectFunc();
    }
  );
  async function selectFunc(){
    const selectBox = document.getElementsByClassName("semi-form-field-main");
    selectBox[0].style.visibility = 'hidden';
    await getKGname();
    nextTick(() => {
      console.log('TreeSelect 数据已更新:', treeData.value);
      selectBox[0].style.visibility = 'visible';
    });
  }
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

  const handleFileChange =  () => {
    uploadFlag.value = true;
    console.log("uploadFlag",uploadFlag.value);

  };
  // 只上传知识库名称
  const handleSubmit = (values) => {
    console.log("Form",values.tree);
    console.log(uploadFlag.value);
    if (uploadFlag.value == false){
      Toast.error('请上传文件');
    }
    else{
      console.log("上传文件");
      Notification.info({
        title: '上传文件至知识库',
        content: '请稍等,上传时不要关闭此页面',
        duration: 0,
        theme: 'light',
      });
      const data = {
        KGName: values.tree,
      };
      console.log(data);
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
    
  };
  };




  </script>
  
  <style scoped>
  div.semi-form-field{
    width:400px;
    font-size: 12px;
    font-weight: bold;
  }
  </style>
  