<template>
  <header class="app-header">
    <div class="header-left">
      <h1 class="logo">旅游客服 Copilot</h1>
    </div>
    <div class="header-center">
      <el-input
        v-model="ticketInput"
        placeholder="输入工单号，如 TK-20240728-001"
        size="large"
        class="ticket-input"
        clearable
        @keyup.enter="analyze"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-button type="primary" size="large" @click="analyze" :loading="loading">
        分析
      </el-button>
    </div>
    <div class="header-right">
      <span v-if="store.result" class="ticket-info">
        {{ store.result.ticket_id }}
      </span>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Search } from "@element-plus/icons-vue";
import { useCopilotStore } from "../stores/copilot";

const props = defineProps<{ loading: boolean }>();
const emit = defineEmits<{ analyze: [ticketId: string] }>();

const store = useCopilotStore();
const ticketInput = ref("");

function analyze() {
  const id = ticketInput.value.trim();
  if (id) {
    emit("analyze", id);
  }
}
</script>

<style scoped>
.app-header {
  height: 64px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 24px;
}

.logo {
  font-size: 20px;
  font-weight: 600;
  color: #409eff;
  white-space: nowrap;
}

.header-center {
  flex: 1;
  display: flex;
  gap: 12px;
  max-width: 600px;
  margin: 0 auto;
}

.ticket-input {
  flex: 1;
}

.ticket-info {
  font-size: 14px;
  color: #909399;
}
</style>
