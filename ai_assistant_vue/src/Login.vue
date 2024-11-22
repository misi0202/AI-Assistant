<script setup>
import LoginBox from './components/Login.vue'

</script>

<template>
<div class="robot">
<LoginBox></LoginBox>
</div>

</template>



<style>
.robot{
    width: 2000px;
    height: 926px;
    background: url('/images/robot.jpg');
    background-repeat: no-repeat; /* 禁止重复 */
    background-size: cover;       /* 图片按比例缩放，覆盖整个容器 */
    background-position: center;  /* 图片居中对齐 */
}
.form-wrapper{
    position: absolute;
    top: 200px;
    left: 200px;
}
</style>


