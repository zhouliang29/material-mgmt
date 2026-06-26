<script setup>
import { useUserStore } from './stores/user'

const userStore = useUserStore()
</script>

<template>
  <router-view />
</template>

<style>
/* 全局样式在 style.css */
</style>
