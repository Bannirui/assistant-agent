<template>
  <div class="admin-page">
    <div class="page-header">
      <h2>{{ isNew ? "新增文档" : "编辑文档" }}</h2>
      <el-button @click="$router.push('/admin/knowledge')">返回列表</el-button>
    </div>

    <el-form :model="form" label-width="80px" v-loading="saving">
      <el-form-item label="标题">
        <el-input v-model="form.title" placeholder="文档标题" />
      </el-form-item>
      <el-form-item label="来源">
        <el-input v-model="form.source" placeholder="如 手动上传 / Confluence" />
      </el-form-item>
      <el-form-item label="内容">
        <el-input v-model="form.content" type="textarea" :rows="20" placeholder="Markdown 格式，支持 # ## ### 标题和空行分段" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { getDoc, createDoc, updateDoc } from "../../api/knowledge";

const route = useRoute();
const router = useRouter();

const docId = computed(() => Number(route.params.id));
const isNew = computed(() => !route.params.id || route.params.id === "new");
const saving = ref(false);

const form = ref({ title: "", content: "", source: "" });

onMounted(async () => {
  if (!isNew.value) {
    const doc = await getDoc(docId.value);
    form.value = { title: doc.title, content: doc.content, source: doc.source };
  }
});

async function handleSave() {
  saving.value = true;
  try {
    if (isNew.value) {
      await createDoc(form.value);
      ElMessage.success("创建成功");
    } else {
      await updateDoc(docId.value, form.value);
      ElMessage.success("更新成功");
    }
    router.push("/admin/knowledge");
  } catch (e: any) {
    ElMessage.error(e?.message || "保存失败");
  } finally {
    saving.value = false;
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
  margin-bottom: 24px;
}

.page-header h2 {
  font-size: 20px;
  font-weight: 600;
}

.el-form {
  max-width: 900px;
}
</style>
