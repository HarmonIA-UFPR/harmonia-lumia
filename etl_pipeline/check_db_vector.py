"""
Diagnostico da memoria vetorial - HarmonIA.
Verifica:
1. Recursos do sistema
2. Conectividade com Weaviate
3. Existencia da colecao
4. Sanidade semantica (LaBSE -> Weaviate)
5. Distribuicao por complexidade
6. Contagem esperada de objetos persistidos
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import warnings
from collections import Counter
from pathlib import Path

import psutil
import weaviate

from config.config import settings
from etl_pipeline.embedding import gerar_embedding_unico


warnings.filterwarnings("ignore", category=DeprecationWarning)

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_JSONL_PATH = BASE_DIR / "sql_data.jsonl"


def verificar_recursos() -> None:
    mem = psutil.virtual_memory()
    cpu_pct = psutil.cpu_percent(interval=1)

    print(f"[*] RAM disponivel: {mem.available / (1024**3):.2f} GB")
    print(f"[*] RAM total: {mem.total / (1024**3):.2f} GB")
    print(f"[*] Uso de CPU: {cpu_pct}%")
    print("-" * 60)


def criar_cliente_weaviate() -> weaviate.WeaviateClient:
    connection_params = weaviate.connect.ConnectionParams.from_params(
        http_host=settings.WEAVIATE_HOST,
        http_port=settings.WEAVIATE_HTTP_PORT,
        http_secure=False,
        grpc_host=settings.WEAVIATE_HOST,
        grpc_port=settings.WEAVIATE_GRPC_PORT,
        grpc_secure=False,
    )
    return weaviate.WeaviateClient(connection_params)


def verificar_colecao(client: weaviate.WeaviateClient) -> tuple[object, int]:
    if not client.collections.exists(settings.COLLECTION_NAME):
        raise RuntimeError(f"Colecao '{settings.COLLECTION_NAME}' nao encontrada.")

    colecao = client.collections.get(settings.COLLECTION_NAME)
    res_count = colecao.aggregate.over_all(total_count=True)
    count = int(res_count.total_count or 0)

    print(f"[+] Colecao: {settings.COLLECTION_NAME}")
    print(f"[+] Total de registros: {count}")
    print("-" * 60)

    return colecao, count


def teste_semantico(colecao: object) -> None:
    print("[*] Testando recuperacao semantica...")
    query_teste = "Ferramenta de edicao de texto"
    query_vector = gerar_embedding_unico(query_teste)

    if not query_vector:
        raise RuntimeError("Falha ao gerar embedding para a consulta semantica.")

    res = colecao.query.near_vector(
        near_vector=query_vector,
        limit=1,
        return_properties=["tool_description", "tool_name", "tool_complexity"],
        return_metadata=weaviate.classes.query.MetadataQuery(distance=True),
    )

    if not res.objects:
        raise RuntimeError("Busca semantica retornou vazio.")

    obj = res.objects[0]
    descricao = str(obj.properties.get("tool_description", ""))[:120]

    print("[+] Busca semantica: OK")
    print(f"    Distancia: {obj.metadata.distance:.4f}")
    print(f"    Ferramenta: {obj.properties.get('tool_name')}")
    print(f"    Complexidade: {obj.properties.get('tool_complexity')}")
    print(f"    Descricao: {descricao}...")
    print("-" * 60)


def distribuicao_complexidade(colecao: object, count: int) -> None:
    print("[*] Distribuicao por complexidade:")
    try:
        limit = min(max(count, 1), 5000)
        resp = colecao.query.fetch_objects(
            limit=limit,
            return_properties=["tool_complexity"],
        )
        grupos = Counter(
            str(obj.properties.get("tool_complexity"))
            for obj in resp.objects
            if obj.properties.get("tool_complexity") is not None
        )
        if not grupos:
            print("    [!] Sem dados de complexidade para exibir.")
        else:
            for nivel, total in sorted(grupos.items(), key=lambda item: item[0]):
                print(f"    Nivel {nivel}: {total} ferramentas")
    except Exception as exc:
        print(f"    [!] Nao foi possivel agrupar: {exc}")
    print("-" * 60)


def contar_registros_jsonl(caminho: Path) -> int:
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo JSONL nao encontrado: {caminho}")

    count = 0
    with caminho.open("r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            try:
                item = json.loads(linha)
            except json.JSONDecodeError:
                continue
            if item.get("tool_description") and item.get("tool_uuidv7"):
                count += 1
    return count


def executar_diagnostico(expected_count: int | None) -> None:
    print("\n" + "=" * 60)
    print(f"HARMONIA - DIAGNOSTICO ({'DEBUG' if settings.DEBUG else 'PROD'})")
    print("=" * 60)

    verificar_recursos()
    client = criar_cliente_weaviate()

    try:
        client.connect()
        if not client.is_ready():
            raise RuntimeError("Weaviate esta online, mas nao esta pronto.")

        print("[+] Conexao Weaviate: OK")
        print("-" * 60)

        colecao, count = verificar_colecao(client)

        if expected_count is not None and count != expected_count:
            raise RuntimeError(
                "Quantidade persistida divergente. "
                f"Esperado: {expected_count}, encontrado: {count}."
            )

        if count > 0:
            teste_semantico(colecao)
            distribuicao_complexidade(colecao, count)
        else:
            raise RuntimeError("Colecao vazia. Nada para diagnosticar.")

    finally:
        client.close()
        print("=" * 60)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Diagnostico da memoria vetorial no Weaviate."
    )
    parser.add_argument(
        "--expected-count",
        type=int,
        default=None,
        help="Quantidade esperada de registros na colecao.",
    )
    parser.add_argument(
        "--expected-from-jsonl",
        action="store_true",
        help="Calcula a contagem esperada a partir de etl_pipeline/sql_data.jsonl.",
    )
    parser.add_argument(
        "--jsonl-path",
        type=Path,
        default=DEFAULT_JSONL_PATH,
        help="Caminho do JSONL usado para calcular a contagem esperada.",
    )
    return parser


def main() -> None:
    if __name__ == "__main__":
        mp.set_start_method("spawn", force=True)

    args = build_parser().parse_args()
    expected_count = args.expected_count

    if args.expected_from_jsonl:
        expected_count = contar_registros_jsonl(args.jsonl_path.resolve())
        print(f"[*] Contagem esperada pelo JSONL: {expected_count}")
        print("-" * 60)

    executar_diagnostico(expected_count=expected_count)


if __name__ == "__main__":
    main()
