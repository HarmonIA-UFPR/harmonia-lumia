# etl_pipeline/quantize_labse.py

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import json
from pathlib import Path
from transformers import AutoTokenizer
from optimum.intel.openvino import OVModelForFeatureExtraction, OVQuantizer
from datasets import Dataset


def carregar_textos_reais_jsonl(caminho_arquivo: str, limite: int | None = None):
    """
    Carrega apenas o campo 'tool_description'
    do arquivo jsonl para calibração INT8.
    """

    textos = []
    caminho = Path(caminho_arquivo).resolve()

    print(f"[*] Lendo dados reais de: {caminho}")

    with caminho.open("r", encoding="utf-8") as f:
        for linha in f:
            registro = json.loads(linha)
            descricao = registro.get("tool_description")

            if descricao:
                textos.append(descricao)

            if limite and len(textos) >= limite:
                break

    print(f"[+] {len(textos)} descrições carregadas para calibração")
    return textos


def quantizar_labse_int8():

    model_path = Path("modelos/LaBSE").resolve()
    save_path = Path("modelos/LaBSE_int8").resolve()
    jsonl_path = Path("etl_pipeline/sql_data.jsonl").resolve()

    print("[*] Exportando modelo OpenVINO FP32...")

    tokenizer = AutoTokenizer.from_pretrained(str(model_path))

    model = OVModelForFeatureExtraction.from_pretrained(
        str(model_path),
        export=True,
    )

    print("[*] Carregando dataset real para calibração...")

    calibration_texts = carregar_textos_reais_jsonl(
        jsonl_path,
        limite=1000  
    )

    dataset = Dataset.from_dict({"text": calibration_texts})

    def tokenize_function(example):
        return tokenizer(
            example["text"],
            padding="max_length",
            truncation=True,
            max_length=256,  
        )

    dataset = dataset.map(tokenize_function, batched=True)
    dataset.set_format("torch")

    print("[*] Preparando quantizador...")

    quantizer = OVQuantizer.from_pretrained(model)

    print("[*] Aplicando quantização INT8...")

    quantizer.quantize(
        calibration_dataset=dataset,
        save_directory=str(save_path),
    )

    tokenizer.save_pretrained(str(save_path))

    print(f"[+] Modelo INT8 salvo em: {save_path}")


if __name__ == "__main__":
    quantizar_labse_int8()