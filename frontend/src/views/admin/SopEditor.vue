<template>
  <div class="admin-page">
    <div class="page-header">
      <h2>{{ isNew ? "新增 SOP" : "编辑 SOP" }}</h2>
      <el-button @click="$router.push('/admin/sop')">返回列表</el-button>
    </div>

    <el-form :model="form" label-width="120px" v-loading="saving">
      <el-form-item label="SOP ID">
        <el-input v-model="form.id" :disabled="!isNew" placeholder="如 FLIGHT_REFUND_DISPUTE" />
      </el-form-item>
      <el-form-item label="品类">
        <el-select v-model="form.category">
          <el-option label="机票" value="机票" />
          <el-option label="酒店" value="酒店" />
          <el-option label="火车" value="火车" />
          <el-option label="打车" value="打车" />
        </el-select>
      </el-form-item>
      <el-form-item label="适用问题">
        <el-input v-model="issueTypes" placeholder="逗号分隔，如: 退差价,价格争议" />
      </el-form-item>
      <el-form-item label="处理步骤">
        <el-input v-model="form.steps" type="textarea" :rows="4" placeholder="每行一个步骤" />
      </el-form-item>
      <el-form-item label="补偿规则">
        <el-input v-model="form.compensation_rules" type="textarea" :rows="4" placeholder='JSON数组: [{"condition":"...","action":"..."}]' />
      </el-form-item>
      <el-form-item label="话术模板">
        <el-input v-model="form.templates" type="textarea" :rows="4" placeholder='JSON对象: {"key":"文本"}' />
      </el-form-item>
      <el-form-item label="操作按钮">
        <el-input v-model="form.suggested_actions" type="textarea" :rows="3" placeholder='JSON数组: [{"type":"...","label":"..."}]' />
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
import { getSop, createSop, updateSop } from "../../api/sop";

const route = useRoute();
const router = useRouter();

const sopId = computed(() => route.params.id as string);
const isNew = computed(() => !sopId.value || sopId.value === "new");
const saving = ref(false);

const issueTypes = ref("");

const form = ref<Record<string, any>>({
  id: "",
  category: "机票",
  issue_types: [],
  steps: [],
  compensation_rules: [],
  templates: {},
  suggested_actions: [],
});

onMounted(async () => {
  if (!isNew.value) {
    const sop = await getSop(sopId.value);
    Object.assign(form.value, sop);
    issueTypes.value = (sop.issue_types || []).join(",");
    form.value.steps = (sop.steps || []).join("\n");
    form.value.compensation_rules = JSON.stringify(sop.compensation_rules || [], null, 2);
    form.value.templates = JSON.stringify(sop.templates || {}, null, 2);
    form.value.suggested_actions = JSON.stringify(sop.suggested_actions || [], null, 2);
  }
});

async function handleSave() {
  saving.value = true;
  try {
    const payload = {
      ...form.value,
      issue_types: issueTypes.value.split(",").map((s: string) => s.trim()).filter(Boolean),
      steps: form.value.steps ? form.value.steps.split("\n").filter(Boolean) : [],
      compensation_rules: JSON.parse(form.value.compensation_rules || "[]"),
      templates: JSON.parse(form.value.templates || "{}"),
      suggested_actions: JSON.parse(form.value.suggested_actions || "[]"),
    };

    if (isNew.value) {
      await createSop(payload);
      ElMessage.success("创建成功");
      router.push(`/admin/sop/${payload.id}`);
    } else {
      await updateSop(sopId.value, payload);
      ElMessage.success("更新成功");
    }
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
  max-width: 800px;
}
</style>
