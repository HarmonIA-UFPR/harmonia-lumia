DO $$
BEGIN
    INSERT INTO agente.history_chat_v2  (
    	his_session_uuidv7,
    	his_chat_uuidv7,
    	his_user_uuidv7,
    	his_user_profile,
    	his_user_prompt,
    	his_tool_recom_jsonb,
    	his_tool_recom_composite_type,
    	his_llm_response,
    	his_timestamp
    ) 
    VALUES
    ('922ac61d-3d98-4564-b4c9-c64ae9fe4ae6'::uuid,
    '019c9f8b-d19e-797f-a255-728af58c1abc'::uuid,
    '019c9f4c-3de9-7583-8f66-f48821299fd1'::uuid,
    1,
    'Quero ferramentas para editar vídeos',
    '[{"tool_uuidv7": "019c7b2c-0984-7279-888b-081cef3f0532","score": 0.7890047430992126},
     {"tool_uuidv7": "019c7b2c-0991-7774-93ea-b9260d064d37","score": 0.7849726676940918}, 
    {"tool_uuidv7": "019c7b2c-0c28-7cef-9416-9e939a9e724f","score": 0.7826951742172241}]'::jsonb,
     ARRAY[('019c7b2c-0984-7279-888b-081cef3f0532'::uuid, 0.79)::agente.tool_recommendation,
            ('019c7b2c-0991-7774-93ea-b9260d064d37'::uuid, 0.78)::agente.tool_recommendation,
            ('019c7b2c-0c28-7cef-9416-9e939a9e724f'::uuid, 0.78)::agente.tool_recommendation
     ],
     'As ferramentas selecionadas são adequadas para ajudar o usuário a editar vídeos. Cleanup.pictures é uma ferramenta simples para remover objetos e imperfeições em imagens, útil para preparar vídeos. Cocounsel AI pode auxiliar no processo de análise de documentos e geração de textos jurídicos, mas requer conhecimento específico. Runway ML é uma plataforma completa com várias ferramentas de criação de vídeo, ideal para quem deseja editar vídeos rapidamente.',
     '2026-02-27 11:41:06.462099-03'
     );
    
    RAISE NOTICE 'Contexto 2: Insert(s) realizado(s) com sucesso.'; 

END $$;

