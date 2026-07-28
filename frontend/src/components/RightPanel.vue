<template>
  <div class="panel right-panel">
    <div class="panel-title">Copilot 分析结果</div>
    <div class="analysis-area">
      <div v-if="store.loading" class="loading-state">
        <el-icon class="loading-icon" :size="32"><Loading /></el-icon>
        <p>AI 分析中...</p>
      </div>

      <div v-else-if="!store.result" class="empty-state">
        <el-icon :size="48"><MagicStick /></el-icon>
        <p>分析结果将显示在这里</p>
      </div>

      <div v-else class="result-content">
        <!-- 意图和风险 -->
        <div class="section intents-section">
          <div class="intent-tag">
            <el-tag type="success" size="large">
              意图: {{ store.result.analysis.intent || "待分析" }}
            </el-tag>
          </div>
          <div class="emotion-info">
            <span class="emotion-label">客户情绪:</span>
            <el-tag :type="emotionTagType" size="small">
              {{ store.result.analysis.emotion || "未知" }}
            </el-tag>
          </div>
          <div v-if="store.result.analysis.risk" class="risk-info">
            <span class="risk-label">风险提示:</span>
            <span class="risk-text" :class="riskClass">{{ store.result.analysis.risk }}</span>
          </div>
        </div>

        <!-- 建议回复 -->
        <div class="section">
          <h3 class="section-title">建议回复</h3>
          <div class="reply-template">
            <p>{{ store.result.reply_template }}</p>
          </div>
          <div class="reply-actions">
            <el-button type="primary" size="small" @click="copyReply">
              <el-icon><CopyDocument /></el-icon> 复制
            </el-button>
            <el-button type="success" size="small" @click="editAndSend">
              <el-icon><Edit /></el-icon> 编辑后发送
            </el-button>
          </div>
        </div>

        <!-- 订单快照 -->
        <div v-if="hasReferences" class="section">
          <h3 class="section-title">参考信息</h3>
          <el-card shadow="never" class="ref-card">
            <template v-if="store.result.references.order_summary">
              <div class="ref-item">
                <span class="ref-label">订单:</span>
                <span>{{ store.result.references.order_summary }}</span>
              </div>
            </template>
            <template v-if="store.result.references.customer_info">
              <div class="ref-item">
                <span class="ref-label">客户:</span>
                <span>{{ store.result.references.customer_info }}</span>
              </div>
            </template>
            <template v-if="store.result.references.policy_excerpt">
              <div class="ref-item">
                <span class="ref-label">政策:</span>
                <span>{{ store.result.references.policy_excerpt }}</span>
              </div>
            </template>
          </el-card>
        </div>

        <!-- 建议操作 -->
        <div v-if="store.result.suggested_actions.length > 0" class="section">
          <h3 class="section-title">建议操作</h3>
          <div class="action-buttons">
            <el-button
              v-for="(action, idx) in store.result.suggested_actions"
              :key="idx"
              :type="actionButtonType(action.type)"
              @click="handleAction(action)"
            >
              {{ action.label }}
            </el-button>
          </div>
        </div>

        <!-- 警告 -->
        <div v-if="store.result.warnings.length > 0" class="section">
          <el-alert
            v-for="(w, idx) in store.result.warnings"
            :key="idx"
            :title="w"
            type="warning"
            show-icon
            :closable="false"
            style="margin-bottom: 8px"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { Loading, MagicStick, CopyDocument, Edit } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { useCopilotStore } from "../stores/copilot";

const store = useCopilotStore();

const hasReferences = computed(() => {
  if (!store.result) return false;
  const refs = store.result.references;
  return refs && Object.values(refs).some((v) => v);
});

const emotionTagType = computed(() => {
  const emotion = store.result?.analysis.emotion;
  if (emotion === "愤怒") return "danger";
  if (emotion === "焦虑") return "warning";
  return "info";
});

const riskClass = computed(() => {
  const risk = store.result?.analysis.risk;
  if (risk?.includes("高")) return "risk-high";
  if (risk?.includes("中")) return "risk-medium";
  return "risk-low";
});

function actionButtonType(actionType: string): string {
  if (actionType.includes("escalate")) return "danger";
  if (actionType.includes("refund") || actionType.includes("cancel")) return "warning";
  if (actionType.includes("coupon")) return "success";
  return "primary";
}

function copyReply() {
  if (store.result) {
    navigator.clipboard.writeText(store.result.reply_template);
    ElMessage.success("已复制到剪贴板");
  }
}

function editAndSend() {
  if (store.result) {
    const filled = store.fillReplyTemplate(store.result.reply_template);
    ElMessage.info("回复已填充到左侧输入框");
  }
}

function handleAction(action: { type: string; label: string }) {
  ElMessage.success(`执行操作: ${action.label}`);
}
</script>

<style scoped>
.right-panel {
  flex: 1;
  min-width: 500px;
}

.panel {
  display: flex;
  flex-direction: column;
  background: #fff;
}

.panel-title {
  padding: 16px 20px;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #e4e7ed;
}

.analysis-area {
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

.result-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section {
  margin-bottom: 8px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid #ebeef5;
}

.intents-section {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.emotion-label,
.risk-label {
  font-size: 13px;
  color: #909399;
  margin-right: 4px;
}

.risk-text {
  font-size: 14px;
  font-weight: 500;
}

.risk-high {
  color: #f56c6c;
}

.risk-medium {
  color: #e6a23c;
}

.risk-low {
  color: #67c23a;
}

.reply-template {
  background: #f5f7fa;
  border-radius: 6px;
  padding: 14px 16px;
  font-size: 14px;
  line-height: 1.7;
  margin-bottom: 10px;
}

.reply-actions {
  display: flex;
  gap: 8px;
}

.ref-card {
  background: #fafafa;
}

.ref-item {
  display: flex;
  gap: 8px;
  padding: 6px 0;
  font-size: 13px;
  border-bottom: 1px solid #ebeef5;
}

.ref-item:last-child {
  border-bottom: none;
}

.ref-label {
  font-weight: 600;
  color: #606266;
  white-space: nowrap;
  min-width: 48px;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
