-- ============================================================================
-- CONTEXTO 1: CRIAÇÃO DOS ESQUEMAS (ATÔMICO)
-- ============================================================================
DO $$
BEGIN
    -- Criação dos esquemas lógicos para separação de contexto
    CREATE SCHEMA IF NOT EXISTS harmonia;
    
    RAISE NOTICE 'Contexto 1: Esquemas criados com sucesso.';
END $$;

-- ============================================================================
-- CONTEXTO 2: CRIAÇÃO DAS TABELAS SEM RESTRIÇÕES (ATÔMICO)
-- ============================================================================
DO $$
BEGIN
    -- 1. Tabela USER (Esquema: harmonia)
    CREATE TABLE IF NOT EXISTS harmonia.user (
        user_uuidv7        uuid NOT NULL DEFAULT uuidv7(),
        user_fullname      text NOT NULL,
        user_email         text NOT NULL,
        user_profile       integer NOT NULL,
        user_password_hash text NOT NULL
    );

    -- 2. Tabela TOOL (Esquema: harmonia)
    CREATE TABLE IF NOT EXISTS harmonia.tool (
        tool_uuidv7             uuid NOT NULL DEFAULT uuidv7(),
        tool_name               text NOT NULL,
        tool_description        text NOT NULL,
        tool_data_prog          boolean NOT NULL, -- Assumindo data/hora
        tool_official_link      text NULL,
        tool_repository_link    text NULL,
        tool_documentation_link text NULL,
        -- Deve ser igual ao user_profile logicamente
        tool_complexity         integer NOT NULL 
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
    -- Restrições para HARMONIA.USER
    -- ------------------------------------------------------------------------
    -- Primary Key
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'pk_harmonia_user') THEN
        ALTER TABLE harmonia.user 
        ADD CONSTRAINT pk_harmonia_user PRIMARY KEY (user_uuidv7);
    END IF;

    -- Unique Email
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_harmonia_user_email') THEN
        ALTER TABLE harmonia.user 
        ADD CONSTRAINT uq_harmonia_user_email UNIQUE (user_email);
    END IF;


    -- ------------------------------------------------------------------------
    -- Restrições para HARMONIA.TOOL
    -- ------------------------------------------------------------------------
    -- Primary Key
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'pk_harmonia_tool') THEN
        ALTER TABLE harmonia.tool 
        ADD CONSTRAINT pk_harmonia_tool PRIMARY KEY (tool_uuidv7);
    END IF;


    RAISE NOTICE 'Contexto 3: Restrições (PKs, FKs) e Índices aplicados com sucesso.';
END $$;
