# Agente de Correcao e Resumo (LangChain + Groq)

Este agente le uma transcricao em .txt, corrige erros de escrita com base no contexto e gera um resumo claro da mensagem do audio.

## Requisitos
- Python 3.9+
- Chave da Groq (GROQ_API_KEY)

## Instalar dependencias

```powershell
pip install langchain-core langchain-groq
```

Se preferir, adicione ao `requirements.txt` e rode:

```powershell
pip install -r requirements.txt
```

## Configurar chave da Groq

PowerShell:

```powershell
$env:GROQ_API_KEY = "sua_chave_aqui"
```

Opcional: voce pode colocar a chave no arquivo `.env`, mas sera necessario carregar o ambiente antes de rodar o script.

## Rodar

Basico:

```powershell
python src/agent.py --input transcricao.txt
```

Saidas padrao:
- `transcricao_corrigida.txt`
- `resumo.txt`

## Opcoes

```powershell
python src/agent.py --input transcricao.txt --corrected corrigido.txt --summary resumo.txt
python src/agent.py --input transcricao.txt --model llama-3.1-8b-instant --temperature 0.2
```

## Observacoes
- O arquivo de entrada deve estar em UTF-8.
- O agente nao inventa informacoes, apenas corrige e resume o que foi dito.
- Para textos muito longos, pode ser necessario dividir a transcricao.
