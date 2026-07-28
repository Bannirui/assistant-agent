import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      redirect: "/copilot",
    },
    {
      path: "/copilot",
      name: "copilot",
      component: () => import("../views/CopilotView.vue"),
      meta: { title: "客服工作台", role: "agent" },
    },
    {
      path: "/admin/sop",
      name: "sop-list",
      component: () => import("../views/admin/SopList.vue"),
      meta: { title: "SOP 管理", role: "admin" },
    },
    {
      path: "/admin/sop/:id",
      name: "sop-editor",
      component: () => import("../views/admin/SopEditor.vue"),
      meta: { title: "编辑 SOP", role: "admin" },
    },
    {
      path: "/admin/knowledge",
      name: "knowledge-list",
      component: () => import("../views/admin/KnowledgeList.vue"),
      meta: { title: "知识库管理", role: "admin" },
    },
    {
      path: "/admin/knowledge/:id",
      name: "knowledge-editor",
      component: () => import("../views/admin/KnowledgeEditor.vue"),
      meta: { title: "编辑文档", role: "admin" },
    },
  ],
});

// 角色守卫
const currentRole = (): string => localStorage.getItem("role") || "agent";

router.beforeEach((to, _from, next) => {
  const required = to.meta.role as string | undefined;
  if (required && currentRole() !== required) {
    next("/copilot");
  } else {
    next();
  }
});

export default router;
