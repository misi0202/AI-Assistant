<template>
<Nav
  :bodyStyle="{ height: '320px'}"
  :items="navItems"
  :header="header"
  :footer="footer"
  @select="handleSelect"
  @click="handleClick"
/>

</template>

<script lang="jsx">

import { Nav } from '@kousum/semi-ui-vue';
import { IconSemiLogo } from '@kousum/semi-icons-vue';
import { IconDescriptions, IconTree, IconAvatar, IconOverflow,IconBanner,IconForm,IconAccessibility } from '@kousum/semi-icons-lab-vue';

export default {
  components: {
    Nav,
    IconSemiLogo,
    IconDescriptions,
    IconTree,
    IconAvatar,
  },
  data() {
    return {
      navItems: [
        {
          itemKey: 'chat',
          text: '助教对话',
          icon: <IconOverflow />, 
        },
        {
          itemKey: 'config',
          text: '知识库管理',
          icon: <IconBanner />,  
          items: ['创建知识库', '修改知识库','上传文件'],
        },
        {
          itemKey: 'Choose',
          text: '重新选择课程',
          icon: <IconForm />, 
        },
        {
          itemKey: 'user_manage',
          text: '用户管理',
          icon: <IconAccessibility />, 
        }

      ],
      header: {
        text: '东华大学AI助教系统',
      },
      footer: {
        collapseButton: true,
      },
    };
  },
  methods: {
    handleSelect(data) {
      console.log('trigger onSelect: ', data);
    },
    handleClick(data) {
      const key = data.itemKey;
      console.log(key)
      if (key == "config"){
        console.log(key)
      }
      else
      if (key == "创建知识库"){
        this.$router.push({ name: 'CreateKG'});
      }
      else if(key == "chat"){
        this.$router.push({ name: 'Chat'});
      }
      else if(key == "上传文件"){
        this.$router.push({ name: 'Uploadfile'});
      }
      else if(key == "修改知识库"){
        this.$router.push({ name: 'ModifyKG'});
      }
      else if(key == "Choose"){
        this.$router.push({ name: 'Choose'});
      }
      else if(key == "用户管理"){
        this.$router.push({ name: 'user_manage'});
      }
      else {
        this.$router.push({ name: key});
      }

    },
  },
};
</script>

<style scoped>

</style>
