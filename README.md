# pdf2md — PDF → Markdown converter

Interface web local para converter PDFs em Markdown usando OpenDataLoader.

## Instalação

```bash
pip install flask opendataloader-pdf
```

## Como usar

```bash
python app.py
```

Acesse: http://localhost:5000

## Funcionalidades

- Drag-and-drop de PDF
- Modo Local (CPU, sem internet)
- Modo Híbrido IA (melhor para tabelas, OCR, fórmulas)
- Visualização do Markdown gerado
- Copiar para clipboard
- Download do .md
