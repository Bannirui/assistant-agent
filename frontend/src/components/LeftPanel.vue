<template>
  <div class="panel left-panel">
    <div class="panel-title">对话面板</div>
    <div class="conversation-area">
      <div v-if="store.loading" class="loading-state">
        <el-icon class="loading-icon" :size="32"><Loading /></el-icon>
        <p>正在分析工单 {{ store.ticketId }}...</p>
      </div>
      <div v-else-if="store.error" class="error-state">
        <el-alert :title="store.error" type="error" show-icon :closable="false" />
      </div>
      <div v-else-if="store.result" class="conversation-view">
        <div class="message customer-message">
          <div class="message-avatar customer-avatar">客</div>
          <div class="message-bubble customer-bubble">
            <div class="message-sender">客户</div>
            <div class="message-text">{{ store.result.analysis.intent || "查看右侧面板获取详情" }}</div>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        <el-icon :size="48"><ChatDotRound /></el-icon>
        <p>输入工单号开始分析</p>
      </div>
    </div>
    <div class="reply-input-area">
      <el-input
        v-model="replyText"
        type="textarea"
        :rows="3"
        placeholder="编辑回复内容..."
        resize="none"
      />
      <el-button type="primary" :disabled="!replyText.trim()" @click="sendReply">
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Loading, ChatDotRound } from "@element-plus/icons-vue";
import { useCopilotStore } from "../stores/copilot";

const store = useCopilotStore();
const replyText = ref("");

function sendReply() {
  if (replyText.value.trim()) {
    replyText.value = "";
  }
}
</script>

<style scoped>
.left-panel {
  width: 45%;
  min-width: 400px;
}

.panel {
  display: flex;
  flex-direction: column;
  background: #fff;
  border-right: 1px solid #e4e7ed;
}

.panel-title {
  padding: 16px 20px;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #e4e7ed;
}

.conversation-area {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.empty-state,
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
  gap: 12px;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.conversation-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #fff;
  flex-shrink: 0;
}

.customer-avatar {
  background: #67c23a;
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
}

.customer-bubble {
  background: #f0f9eb;
}

.message-sender {
  font-weight: 600;
  margin-bottom: 4px;
  font-size: 13px;
  color: #909399;
}

.reply-input-area {
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.reply-input-area .el-button {
  flex-shrink: 0;
}
</style>
