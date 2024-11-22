<script setup>

import DefaultChat from './components/DefaultChat.vue';
import Nav from './components/Nav.vue'
</script>

<template>
<div class="container">
    <Nav />
<DefaultChat />
</div>


</template>


<style>
    .container{
        display: flex;
        margin-left: 0px;
        margin-right: 0px;
        margin-bottom: 10px;
        margin-top: 10px;
    }
    .semi-chat {
        max-height: 896px;
        overflow-y: auto; /* 使 div 可滚动 */
        background: linear-gradient(to bottom, #f0edf7, #e4eaf7);

    }


</style>
