<template>
  <div id="app-container">
    <AppHeader @analyze="handleAnalyze" :loading="store.loading" />
    <div class="workspace">
      <LeftPanel />
      <RightPanel />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useCopilotStore } from "./stores/copilot";
import AppHeader from "./components/AppHeader.vue";
import LeftPanel from "./components/LeftPanel.vue";
import RightPanel from "./components/RightPanel.vue";

const store = useCopilotStore();

function handleAnalyze(ticketId: string) {
  store.submitTicket(ticketId);
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
  background: #f5f7fa;
  color: #303133;
}

#app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.workspace {
  flex: 1;
  display: flex;
  overflow: hidden;
}
</style>
