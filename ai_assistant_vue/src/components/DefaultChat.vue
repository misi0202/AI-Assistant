<script setup>
document.body.style.backgroundImage = 'linear-gradient(to bottom, #f0edf7, #e4eaf7)';; 
import { ref } from 'vue';
import { Chat, Notification } from '@kousum/semi-ui-vue';
import axios from 'axios'; 
import Navi from './Nav.vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

const roleInfo = {
  user: {
    name: 'User',
    avatar: 'https://lf3-static.bytednsdoc.com/obj/eden-cn/ptlz_zlp/ljhwZthlaukjlkulzlp/docs-icon.png'
  },
  assistant: {
    name: 'Assistant',
    avatar: 'https://lf3-static.bytednsdoc.com/obj/eden-cn/ptlz_zlp/ljhwZthlaukjlkulzlp/other/logo.png'
  },
  system: {
    name: 'System',
    avatar: 'https://lf3-static.bytednsdoc.com/obj/eden-cn/ptlz_zlp/ljhwZthlaukjlkulzlp/other/logo.png'
  }
};

const commonOuterStyle = {
  border: '1px solid var(--semi-color-border)',
  borderRadius: '16px',

};

let id = 0;

function getId() {
  return `id-${id++}`;
}
const store = useStore();
// 获取选择的知识库名称
function getSharedKGName() {
      return store.state.chatCourse; // 获取 Vuex state 中的 sharedMessage
}
const CourseName = getSharedKGName();
const router = useRouter();
console.log("当前课程名：",CourseName);
if (CourseName == "none"){
  Notification.warning({
        title: '提示',
        content: '请先选择课程',
        position: 'top',
        theme: 'light',
      });
  router.push({ name: 'Choose' });
}
const defaultMessage = [
  {
    role: 'system',
    id: '1',
    createAt: 1715676751919,
    content: "欢迎使用东华大学"+CourseName+"AI助教",
  }
];
function scrollToBottom() {
      // 获取 div 的引用
      const contentDiv = this.$refs.contentDiv;
      // 将 scrollTop 设置为最大值，实现自动滚动到底部
      contentDiv.scrollTop = contentDiv.scrollHeight;
    }

const message = ref(defaultMessage);
const mode = ref('bubble');
const align = ref('leftRight');

const onAlignChange = (e) => {
  align.value = e.target.value;
};

const onModeChange = (e) => {
  mode.value = e.target.value;
};

const onMessageSend = (user_input, attachment) => {
  const qa_data = {
    course_name: CourseName,
    user_input: user_input,
    history: message.value,
  };
  console.log(qa_data);
  let newAssistantMessage; 
  let newLoadingMessage;
  newLoadingMessage =  {
    id: 'loading',
    role: 'assistant',
    status: 'loading'
  }
  message.value = [...message.value, newLoadingMessage];
  axios.post('http://127.0.0.1:5000/api/knowledge_qa', qa_data)
    .then(res => {
      console.log(res);
      const response = res.data.response;
      // 提取chunks
      const chunks = res.data.chunks;


      const newChunkMessage = chunks.map(item => `| 来源:${item.source.replace(/\n/g, '')} |\n|------|\n| 内容:${item.content.replace(/\n/g, '')} |\n\n`);
      console.log(newChunkMessage);
      
      const finalMessage = response + '\n\n---\n\n' + newChunkMessage.join('');;
      console.log(finalMessage);
      newAssistantMessage = {
        role: 'assistant',
        id: getId(),
        createAt: Date.now(),
        content: finalMessage,
      };
      setTimeout(() => {
        // remove loading message
        message.value = message.value.filter(item => item.id !== 'loading');
        message.value = [...message.value, newAssistantMessage];
      }, 200);
      scrollToBottom();

    })
    .catch(err => {
      console.log('Error:', err);
    });
};


const onChatsChange = (chats) => {
  message.value = chats;
};

const onMessageReset = (e) => {
  setTimeout(() => {
    const lastMessage = message.value[message.value.length - 1];
    const newLastMessage = {
      ...lastMessage,
      status: 'complete',
      content: 'This is a mock reset message.',
    };
    message.value = [...message.value.slice(0, -1), newLastMessage];
  }, 200);
};
</script>

<template>

  <div>

    <Chat
      :key="align + mode"
      :align="align"
      :mode="mode"
      :style="commonOuterStyle"
      :chats="message"
      :roleConfig="roleInfo"
      @chatsChange="onChatsChange"
      @messageSend="onMessageSend"
      @messageReset="onMessageReset"
    />
    
  </div>
</template>

<style >


.semi-upload{
  display: none;
}
div#app{
  width: 1560px;
  max-width: 1560px;
  height: 896px;
  padding: 0px;
  margin-left: 0px;
  margin-right: 20px;
  margin-bottom: 20px;
  margin-top: 10px;
}
.semi-chat{
  max-width: 1560px;
  height: 100%;
  width: 1820px;
}

</style>


