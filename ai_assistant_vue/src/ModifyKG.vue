<script setup>
import Modify_kg from './components/Modify_kg.vue'
import Nav from './components/Nav.vue'
</script>

<template>
<div class="container">
    <Nav />
<Modify_kg/>
</div>

</template>



<style>
div.semi-form-field-label-text{
  font-size: 12px;
  font-weight: bold;
}
div.container{
    width: 1800px;
}
div.semi-card-group{
    padding: 20px;
}
div.semi-card{
  width: 300px;
}
body {
  min-height: 100vh;
  background: linear-gradient(to bottom, #f0edf7, #e4eaf7);
  margin: 0;
}


</style>


