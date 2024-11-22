<template>
    <!-- 整体背景 -->
    <div class="login-wrap">
      <!--输入框-->
      <div class="form-wrapper">
        <div class="header">
          AI助教系统登录
        </div>
        <div class="input-wrapper">
          <div class="border-wrapper">
            <input type="text" name="username" placeholder="账号" class="border-item" autocomplete="off" v-model="loginForm.account"/>
          </div>
          <div class="border-wrapper">
            <input type="password" name="password" placeholder="密码" class="border-item" autocomplete="off" v-model="loginForm.passWord"/>
          </div>
        </div>
        <div class="action" >
          <div class="btn" @click="submitForm">登录</div>
        </div>
      </div>
    </div>
  </template>
  <style>
  body{
    background: url('/images/robot.jpg');
    background-repeat: no-repeat; /* 禁止重复 */
    background-size: cover;       /* 图片按比例缩放，覆盖整个容器 */
    background-position: center;  /* 图片居中对齐 */
    }
  </style>
  <style scoped>

  .login-wrap {
    height: 100%;
    font-family: JetBrains Mono Medium;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    /* background-color: #0e92b3; */
    background-size: 100% 100%;
  }
   
  .form-wrapper {
    background-color: rgba(41, 45, 62, 0.8);
    color: #fff;
    border-radius: 2px;
    padding: 50px;
  }
   
  .form-wrapper .header {
    text-align: center;
    font-size: 35px;
    text-transform: uppercase;
    line-height: 100px;
  }
   
  .form-wrapper .input-wrapper input {
    background-color: rgb(41, 45, 62);
    border: 0;
    width: 100%;
    text-align: center;
    font-size: 15px;
    color: #fff;
    outline: none;
  }
   
  .form-wrapper .input-wrapper input::placeholder {
    text-transform: uppercase;
  }
   
  .form-wrapper .input-wrapper .border-wrapper {
    background-image: linear-gradient(to right, #e8198b, #0eb4dd);
    width: 100%;
    height: 50px;
    margin-bottom: 20px;
    border-radius: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
   
  .form-wrapper .input-wrapper .border-wrapper .border-item {
    height: calc(100% - 4px);
    width: calc(100% - 4px);
    border-radius: 30px;
  }
   
  .form-wrapper .action {
    display: flex;
    justify-content: center;
  }
   
  .form-wrapper .action .btn {
    width: 60%;
    text-transform: uppercase;
    border: 2px solid #0e92b3;
    text-align: center;
    line-height: 50px;
    border-radius: 30px;
    cursor: pointer;
  }
   
  .form-wrapper .action .btn:hover {
    background-image: linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%);
  }
   
  .form-wrapper .icon-wrapper {
    text-align: center;
    width: 60%;
    margin: 0 auto;
    margin-top: 20px;
    border-top: 1px dashed rgb(146, 146, 146);
    padding: 20px;
  }
   
  .form-wrapper .icon-wrapper i {
    font-size: 20px;
    color: rgb(187, 187, 187);
    cursor: pointer;
    border: 1px solid #fff;
    padding: 5px;
    border-radius: 20px;
  }
   
  .form-wrapper .icon-wrapper i:hover {
    background-color: #0e92b3;
  }
  </style>

  <script>
  import { Toast} from '@kousum/semi-ui-vue';
  import { mapMutations } from "vuex";
  import axios from 'axios'; 
 
export default {
  name: "Login",
  data: function () {
    return {
      loginForm: {
        account: "",
        passWord: "",
      },
      loginRules: {
        account: [{ required: true, message: "请输入账号", trigger: "blur" }],
        passWord: [{ required: true, message: "请输入密码", trigger: "blur" }],
      },

      isLoggedIn: false
    };
  },
 
  methods: {
    ...mapMutations(["changeLogin"]),
    submitForm() {
      const userAccount = this.loginForm.account;
      const userPassword = this.loginForm.passWord;
      if (!userAccount) {
        Toast.info('账号不能为空！');
      }
      if (!userPassword) {
        Toast.info('密码不能为空！');
      }
      const data = {
        username: userAccount,
        passwd: userPassword,
      };
      axios.post('http://127.0.0.1:5000/api/login_check', data)
      .then(res => {
        if (res.data == "True"){
            this.isLoggedIn = true;
            document.body.style.backgroundImage = 'linear-gradient(to bottom, #f0edf7, #e4eaf7)';            
            this.$router.push({ name: 'Choose' }); // 跳转到 Choose 页面
        }
        else{
            Toast.info('账号或密码错误！');
        }

        console.log(res.data);
        })

      .catch(err => {
        console.error('Error:', err);
    });

      
    },
  },
};
</script>