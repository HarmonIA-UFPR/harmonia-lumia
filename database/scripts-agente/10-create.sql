-- ============================================================================
-- CONTEXTO 1: CRIAÇÃO DOS ESQUEMAS (ATÔMICO)
-- ============================================================================
DO $$ 
BEGIN 
    -- Criação dos esquemas lógicos para separação de contexto
    CREATE SCHEMA IF NOT EXISTS agente;
    
    RAISE NOTICE 'Contexto 1: Esquemas criados com sucesso.';
END $$;


DO $$ 
BEGIN 
    -- Criação do composite type
    CREATE TYPE agente.tool_recommendation AS (
        tool_uuid uuid,
        score      numeric(3,2)
    );
END $$;

-- ============================================================================
-- CONTEXTO 2: CRIAÇÃO DAS TABELAS SEM RESTRIÇÕES (ATÔMICO)
-- ============================================================================
DO $$ 
BEGIN 
    -- 1. Tabela HISTORY_CHAT (Esquema: agente)
    CREATE TABLE IF NOT EXISTS agente.history_chat (
        his_session_uuid     uuid NOT NULL,
        his_chat_uuidv7      uuid NOT NULL DEFAULT uuidv7(),
        his_user_uuid        uuid NOT NULL,
        his_user_prompt      text,
        his_tool_recom_jsonb jsonb, -- Array de objetos JSON
        his_tool_recom_composite_type agente.tool_recommendation[],
        hist_llm_response    text,
        hist_timestamp       timestamp with time zone DEFAULT now()
    );

    RAISE NOTICE 'Contexto 2: Tabelas criadas (sem restrições de chave).';
END $$;

-- ============================================================================
-- CONTEXTO 3: APLICAÇÃO DAS RESTRIÇÕES E ALTERAÇÕES (ATÔMICO)
-- Aqui aplicamos PKs, FKs e Uniques.
-- ============================================================================
DO $$ 
BEGIN 
    -- ------------------------------------------------------------------------
    -- Restrições para AGENTE.HISTORY_CHAT
    -- ------------------------------------------------------------------------
    -- Primary Key
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'pk_agente_history_chat') THEN
        ALTER TABLE agente.history_chat 
        ADD CONSTRAINT pk_agente_history_chat PRIMARY KEY (his_chat_uuidv7);
    END IF;



    -- Índice GIN para performance no JSONB (Opcional, mas recomendado para arrays)
    CREATE INDEX IF NOT EXISTS idx_history_tools_jsonb 
    ON agente.history_chat USING GIN (his_tool_recom_jsonb);

    RAISE NOTICE 'Contexto 3: Restrições (PKs, FKs) e Índices aplicados com sucesso.';
END $$;
