![Texto HarmonIA (fundo azul)](app-harmonia/frontend/public/images/texto-bg-azul.jpg)


Repositório com a versão estável do projeto HarmonIA LUMIA (Fase 1 - protótipo), incluindo bootstrap completo da infraestrutura, pipeline ETL e subida das aplicações.

## Requisitos obrigatórios

- Shell: `bash`
- Ripgrep: `latest`
- Python: `3.12`

> O script `./harmonia` foi escrito para execução em `bash` e valida a versão do Python como `3.12`.


## Help do script `harmonia`

Saída de `./harmonia --help`:

```text
Uso:
  ./harmonia [OPCAO]

Descricao:
  Executa o bootstrap do projeto HarmonIA em modo modular, com execucao
  e teste para cada etapa.

Opcoes principais:
  -a, --all              Executa todo o pipeline (passos 1 a 5)
  -c, --core             Passo 1: sobe infraestrutura base
  -p, --python           Passo 2: valida versao do Python
  -v, --venv             Passo 3.0: cria e configura venv + Poetry
  -e, --etl              Passo 3 completo (3.1 a 3.6)

Opcoes ETL detalhadas:
  -l, --labse-download   Passo 3.1: download do LaBSE
  -L, --labse-quantize   Passo 3.2: quantizacao do LaBSE
  -q, --qwen-download    Passo 3.3: download do Qwen
  -Q, --qwen-quantize    Passo 3.4: quantizacao do Qwen
  -f, --cleanup-fp32     Passo 3.5: remove modelos FP32
  -i, --ingest           Passo 3.6: ingestao no Weaviate

Opcoes finais:
  -r, --cleanup-venv     Passo 4: remove ambiente virtual
  -s, --apps             Passo 5: sobe app, agente e UI
  -h, --help             Exibe este menu de ajuda

Exemplos:
  ./harmonia --all
  ./harmonia -e
  ./harmonia --qwen-quantize
```

## Execução

Execução completa:

```bash
./harmonia --all
```

Execução por etapas:

```bash
# Passo 1
./harmonia --core

# Passo 2
./harmonia --python

# Passo 3.0
./harmonia --venv

# Passo 3 completo (3.1 a 3.6)
./harmonia --etl

# Passos ETL detalhados
./harmonia --labse-download
./harmonia --labse-quantize
./harmonia --qwen-download
./harmonia --qwen-quantize
./harmonia --cleanup-fp32
./harmonia --ingest

# Passo 4
./harmonia --cleanup-venv

# Passo 5
./harmonia --apps
```

## Interação com o Assistente de Recomendação de Ferramentas de IA

1. No navegador de sua preferência, acesse:
```bash
http://localhost:55036
```

2. Na tela de boas-vindas, clique em **“Entrar”**.

3. Na tela de login entre com um destes usuários:
   
| e-mail para login           | password      | 
|-----------------------------|---------------|
| beto.beginner1@email.com    | beginner1     |
| ive.intermediate1@email.com | intermediate  |
| alex.advanced1@email.com    | advanced1     |
| elena.expert1@email.com     | expert1       |

4. Para criar um novo chat, no canto inferior esquerdo da barra lateral, clique sobre o nome do usuário (ex.: “Beto”) e, em seguida, selecione a opção **“Novo Chat”**.
   
5. Agora é só solicitar suas recomendações!

Observação:
   
Na base de dados referente a esta fase do projeto, foi identificado que algumas fontes apresentam desatualizações, especialmente no que diz respeito a links de páginas oficiais, repositórios e documentações de determinadas ferramentas. Essa situação é relativamente comum em ambientes que lidam com tecnologias dinâmicas, nos quais conteúdos e endereços são frequentemente modificados ou descontinuados ao longo do tempo.

Com o objetivo de garantir a qualidade, a confiabilidade e a atualidade das informações disponibilizadas, mantém-se um processo contínuo de revisão e atualização dessas fontes, o qual se estende e se consolida ao longo das próximas fases do projeto.
