import argparse
import os
import time
from pathlib import Path

from huggingface_hub import snapshot_download


LABSE_IGNORE_PATTERNS = [
    "*.onnx",
    "model.onnx",
    "*.h5",
    "tf_model.h5",
    "*.msgpack",
    "flax_model.msgpack",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download resiliente de modelos Hugging Face para o ETL."
    )
    parser.add_argument("--repo-id", required=True, help="Repo no Hugging Face.")
    parser.add_argument(
        "--local-dir", required=True, help="Diretorio local onde o modelo sera salvo."
    )
    parser.add_argument(
        "--preset",
        choices=["default", "labse"],
        default="default",
        help="Preset de download. 'labse' ignora arquivos grandes desnecessarios.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=6,
        help="Numero maximo de tentativas de download.",
    )
    parser.add_argument(
        "--backoff-seconds",
        type=int,
        default=15,
        help="Tempo base (segundos) para backoff exponencial entre tentativas.",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=2,
        help="Quantidade de workers paralelos no snapshot_download.",
    )
    return parser


def resolve_ignore_patterns(preset: str) -> list[str] | None:
    if preset == "labse":
        return LABSE_IGNORE_PATTERNS
    return None


def download_with_retry(
    repo_id: str,
    local_dir: Path,
    ignore_patterns: list[str] | None,
    retries: int,
    backoff_seconds: int,
    max_workers: int,
) -> None:
    local_dir.mkdir(parents=True, exist_ok=True)
    # Timeout maior reduz falhas intermitentes em links mais lentos.
    os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "120")

    for attempt in range(1, retries + 1):
        print(
            f"[*] Download '{repo_id}' -> '{local_dir}' "
            f"(tentativa {attempt}/{retries})"
        )
        try:
            snapshot_download(
                repo_id=repo_id,
                local_dir=str(local_dir),
                ignore_patterns=ignore_patterns,
                resume_download=True,
                max_workers=max_workers,
            )
            print(f"[+] Download concluido: {repo_id}")
            return
        except Exception as exc:
            if attempt >= retries:
                print(f"[ERRO] Falha final no download de {repo_id}: {exc}")
                raise
            wait_seconds = backoff_seconds * (2 ** (attempt - 1))
            print(
                f"[!] Falha de rede/stream: {exc}\n"
                f"    Retentando em {wait_seconds}s..."
            )
            time.sleep(wait_seconds)


def main() -> None:
    args = build_parser().parse_args()
    ignore_patterns = resolve_ignore_patterns(args.preset)
    download_with_retry(
        repo_id=args.repo_id,
        local_dir=Path(args.local_dir),
        ignore_patterns=ignore_patterns,
        retries=args.retries,
        backoff_seconds=args.backoff_seconds,
        max_workers=args.max_workers,
    )


if __name__ == "__main__":
    main()
