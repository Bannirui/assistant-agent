<template>
  <div class="admin-page">
    <div class="page-header">
      <h2>知识库管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="$router.push('/admin/knowledge/new')">新增文档</el-button>
        <el-button type="success" @click="handleIngest" :loading="ingesting">重建向量索引</el-button>
      </div>
    </div>

    <el-table :data="docs" stripe v-loading="loading" empty-text="暂无文档">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="title" label="标题" min-width="200" />
      <el-table-column prop="source" label="来源" width="140" />
      <el-table-column prop="status" label="状态" width="80" />
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push(`/admin/knowledge/${row.id}`)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { listDocs, deleteDoc, ingestDocs, type KnowledgeDoc } from "../../api/knowledge";

const docs = ref<KnowledgeDoc[]>([]);
const loading = ref(false);
const ingesting = ref(false);

onMounted(fetchDocs);

async function fetchDocs() {
  loading.value = true;
  try {
    docs.value = await listDocs();
  } finally {
    loading.value = false;
  }
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm("确定删除该文档？", "确认", { type: "warning" });
  await deleteDoc(id);
  ElMessage.success("已删除");
  fetchDocs();
}

async function handleIngest() {
  ingesting.value = true;
  try {
    const result = await ingestDocs();
    ElMessage.success(`索引完成，共 ${result.count || 0} 条`);
    fetchDocs();
  } finally {
    ingesting.value = false;
  }
}
</script>

<style scoped>
.admin-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  padding: 24px;
  overflow-y: auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  font-size: 20px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 8px;
}
</style>
