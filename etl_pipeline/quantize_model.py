# etl-pipeline/quantize_model.py

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import gc
from pathlib import Path
import nncf
from transformers import AutoTokenizer
from optimum.intel.openvino import OVModelForCausalLM

def quantizar_qwen():
    model_path = Path("modelos/Qwen").resolve()

    if not model_path.exists():
        raise FileNotFoundError(
            f"Pasta do modelo não encontrada: {model_path}\n"
            "Certifique-se de baixar os pesos do Qwen originais antes de rodar este script."
        )

    save_path = model_path.parent / f"{model_path.name}_int8"
    save_path.mkdir(parents=True, exist_ok=True) # Garante que a pasta pai exista

    print(f"[*] Modelo local FP32: {model_path}")
    print(f"[*] Destino INT8: {save_path}")


    # Carregamento do Tokenizer
    print("[*] Carregando Tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        local_files_only=True
    )

    # Exportação para OpenVINO IR
    print("[*] Carregando e exportando modelo (Isso pode consumir bastante RAM)...")
    model = OVModelForCausalLM.from_pretrained(
        model_path,
        export=True,
        compile=False,       # Importante: não compilar antes da quantização
        local_files_only=True,
        stateful=True        # [CRÍTICO] Melhora drasticamente a performance de LLMs no OpenVINO
    )

    # =========================
    # Quantização Weight-only INT8
    # =========================
    print("[*] Aplicando compressão NNCF INT8 (weight-only)...")

    model.model = nncf.compress_weights(
        model.model,
        mode=nncf.CompressWeightsMode.INT8_ASYM, # INT8 Assimétrico 
        ratio=1.0  # 100% das camadas elegíveis
    )

    # Salvar Modelo
    print(f"[*] Salvando modelo quantizado em: {save_path}...")
    model.save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)


    # Limpeza de Memória
    del model
    gc.collect()

    print(f"[+] Sucesso! Modelo Qwen INT8 otimizado para CPU salvo.")

if __name__ == "__main__":
    quantizar_qwen()
