# Separador de Certificados

Aplicação desktop em Python para separar certificados corporativos em PDFs individuais, com suporte a arquivos NRS e NR-37.

## Funcionalidades
- Processamento individual
- Processamento em lote
- Identificação automática por nome do arquivo
- Geração de relatório de execução
- Exportação de certificados em PDF

## Estrutura do projeto
- `app/config` → configurações
- `app/gui` → interface gráfica
- `app/services` → regras de negócio e processamento
- `app/utils` → utilitários
- `app/validators` → validações auxiliares

## Como executar
```bash
pip install -r requirements.txt
python -m app.main