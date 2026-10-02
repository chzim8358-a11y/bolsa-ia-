# BolsaIA V52 — correções pós-integração do Jarvis

Correções aplicadas:
- Proteção da integração do componente Jarvis: se o iframe de voz/gestos falhar, o Streamlit continua carregando e o comando por texto permanece disponível.
- Correção da Central de Inteligência V49: bloco de apresentação estava dentro do `except` por erro de indentação.
- Inicialização segura dos indicadores da Central para evitar variáveis não definidas quando o Yahoo não retorna dados.
- Título da aplicação atualizado para V52.
- Mantidos os arquivos e funcionalidades existentes; nenhuma dependência nova foi adicionada.

Validação:
- Todos os arquivos Python do projeto foram compilados com sucesso após as correções.
