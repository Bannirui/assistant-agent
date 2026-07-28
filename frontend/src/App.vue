<template>
  <div id="app-wrapper">
    <div class="nav-bar">
      <router-link to="/copilot" class="nav-item" active-class="active">
        客服工作台
      </router-link>
      <router-link to="/admin/sop" class="nav-item" active-class="active">
        SOP 管理
      </router-link>
      <router-link to="/admin/knowledge" class="nav-item" active-class="active">
        知识库管理
      </router-link>
      <div class="nav-right">
        <el-select v-model="role" size="small" style="width: 110px" @change="switchRole">
          <el-option label="客服人员" value="agent" />
          <el-option label="运营人员" value="admin" />
        </el-select>
      </div>
    </div>
    <div class="view-container">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

const role = ref(localStorage.getItem("role") || "agent");
const router = useRouter();

function switchRole(val: string) {
  localStorage.setItem("role", val);
  if (val === "agent") {
    router.push("/copilot");
  }
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

#app-wrapper {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.nav-bar {
  height: 48px;
  background: #304156;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 4px;
}

.nav-item {
  color: #bfcbd9;
  text-decoration: none;
  padding: 0 16px;
  height: 100%;
  display: flex;
  align-items: center;
  font-size: 14px;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.nav-item:hover {
  color: #fff;
  background: rgba(255,255,255,0.05);
}

.nav-item.active {
  color: #fff;
  border-bottom-color: #409eff;
}

.nav-right {
  margin-left: auto;
}

.view-container {
  flex: 1;
  overflow: hidden;
}
</style>
