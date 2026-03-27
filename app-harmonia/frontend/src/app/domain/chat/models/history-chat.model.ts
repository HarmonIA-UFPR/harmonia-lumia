import { UUID7 as uuid7 } from 'uuid7-typed';

export interface ToolRecom {
  tool_uuid: uuid7; // ou uuid7 se preferir manter tipado
  score: number;
}

export interface HistoryChat {
  his_session_uuidv7: uuid7;
  his_chat_uuidv7: uuid7;
  his_user_uuidv7: uuid7;
  his_user_profile: number;
  his_user_prompt: string;
  his_tool_recom_jsonb: ToolRecom[];
  his_llm_response: string;
}

export interface HistoryChatResponse {
  history_chats: HistoryChat[];
  total: number;
  limit: number;
  offset: number;
}

export interface CreateHistoryChatRequest {
  his_session_uuidv7?: uuid7;
  user_profile: number;
  user_prompt: string;
  user_uuid: uuid7;
}
