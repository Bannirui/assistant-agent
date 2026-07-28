<template>
  <div class="admin-page">
    <div class="page-header">
      <h2>SOP 管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="$router.push('/admin/sop/new')">新增 SOP</el-button>
        <el-button @click="handleReload" :loading="reloading">从 DB 重载</el-button>
      </div>
    </div>

    <el-table :data="sops" stripe v-loading="loading" empty-text="暂无 SOP">
      <el-table-column prop="id" label="ID" width="260" />
      <el-table-column prop="category" label="品类" width="80" />
      <el-table-column label="适用问题">
        <template #default="{ row }">
          <el-tag v-for="t in row.issue_types" :key="t" size="small" style="margin-right: 4px">
            {{ t }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push(`/admin/sop/${row.id}`)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { listSops, deleteSop, reloadSops, type SopItem } from "../../api/sop";

const sops = ref<SopItem[]>([]);
const loading = ref(false);
const reloading = ref(false);

onMounted(fetchSops);

async function fetchSops() {
  loading.value = true;
  try {
    sops.value = await listSops();
  } finally {
    loading.value = false;
  }
}

async function handleDelete(id: string) {
  await ElMessageBox.confirm("确定删除该 SOP？", "确认", { type: "warning" });
  await deleteSop(id);
  ElMessage.success("已删除");
  fetchSops();
}

async function handleReload() {
  reloading.value = true;
  try {
    await reloadSops();
    ElMessage.success("已从数据库重载");
    fetchSops();
  } finally {
    reloading.value = false;
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
