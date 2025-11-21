
## Checklist do Projeto bd_CarJa

Prioridade ALTA
- [ ] Migrar `Veiculo.preco` de `CharField` para `DecimalField` com migração de dados e testes de conversão.
- [ ] Aplicar checagens server-side (permissões) nas views de criação/edição/exclusão de veículos (usar `UserPassesTestMixin` ou decorators apropriados).

Prioridade MÉDIA
- [ ] Escrever testes automatizados (unit/integration) para os fluxos de `ComprarVeiculo` e `AlugarVeiculo`.
- [ ] Documentar variáveis de ambiente e criar `ENV.example` com as chaves usadas em `sistema/sistema/settings.py`.
- [ ] Validar e tratar entradas (ex.: `dias` > 0, form validations com mensagens claras).

Prioridade BAIXA
- [ ] Mover estilos inline das miniaturas para uma classe CSS central e ajustar responsividade.
- [ ] Adicionar um script opcional para remover/popular dados de teste (undo/redo para `populate_veiculos`).
- [ ] Adicionar licença e notas de deploy (ex.: como servir `MEDIA` em produção, configurar NGINX/uwsgi/gunicorn).

Melhorias operacionais
- [ ] Adicionar CI (GitHub Actions) para rodar lint, testes e checks de migração.
- [ ] Incluir instruções de backup/restore do banco de dados e de como executar a migração de `preco` com segurança.

Notas técnicas e recomendações
- Fazer backup do banco antes de qualquer migração de dados; testar a migração em ambiente de staging.
- Para migrar `preco`, construir um script que tente parsear valores do formato "R$ 1.234,56" para `Decimal('1234.56')` e registre entradas inválidas para revisão manual.

