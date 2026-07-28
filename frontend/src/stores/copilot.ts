import { defineStore } from "pinia";
import { ref } from "vue";
import { analyzeTicket, type AnalyzeResponse } from "../api";

export const useCopilotStore = defineStore("copilot", () => {
  const ticketId = ref("");
  const loading = ref(false);
  const error = ref("");
  const result = ref<AnalyzeResponse | null>(null);

  async function submitTicket(id: string) {
    ticketId.value = id;
    loading.value = true;
    error.value = "";
    result.value = null;

    try {
      result.value = await analyzeTicket(id);
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e.message || "分析失败";
    } finally {
      loading.value = false;
    }
  }

  const replyVariables = ref<Record<string, string>>({});

  function fillReplyTemplate(template: string): string {
    let filled = template;
    for (const [key, value] of Object.entries(replyVariables.value)) {
      filled = filled.replace(`{${key}}`, value);
    }
    return filled;
  }

  return {
    ticketId,
    loading,
    error,
    result,
    submitTicket,
    replyVariables,
    fillReplyTemplate,
  };
});
