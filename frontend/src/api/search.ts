import apiClient from './client';

export interface SearchRequest {
  query: string;
  cif: string;
  include_global?: boolean;
  top_k?: number;
  similarity_threshold?: number;
  use_guardrails?: boolean;
  prompt_template?: string;
}

export interface AgentActivity {
  name: string;
  status: 'active' | 'completed' | 'failed' | 'skipped';
  execution_time_ms: number;
  data_retrieved?: number;
  confidence?: number;
}

export interface SearchResponse {
  query: string;
  cif: string;
  answer: string;
  citations: Array<{
    source: string;
    title: string;
    text_snippet: string;
    similarity_score: number;
  }>;
  latency_ms: number;
  model_used: string;
  guardrail_status?: any;
  transactions?: any[];
  agent_activity?: AgentActivity[];
  response_type?: string;
  data_sources?: Array<{
    source: string;
    count: number;
    relevance: number;
  }>;
}

export const searchApi = {
  magicSearch: async (data: SearchRequest): Promise<SearchResponse> => {
    const response = await apiClient.post('/search/magic', data);
    return response.data;
  },

  getHistory: async (params?: { cif?: string; limit?: number; offset?: number }) => {
    const response = await apiClient.get('/search/history', { params });
    return response.data;
  },

  aggregateQuery: async (queryType: string, cif: string) => {
    const response = await apiClient.post(`/search/aggregate/${queryType}`, null, {
      params: { cif },
    });
    return response.data;
  },
};