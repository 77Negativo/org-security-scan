-- ============================================================================
-- EXEMPLOS DE QUERIES CUSTOMIZADAS
-- ============================================================================
-- Este arquivo contém exemplos de queries adicionais que você pode usar
-- Copie e adapte conforme suas necessidades

-- 1. Repositórios com muitas issues abertas
-- Identifica repos que podem precisar de atenção
SELECT
  name as "Repositório",
  open_issues_count as "Issues Abertas",
  visibility as "Visibilidade",
  default_branch as "Branch Padrão",
  updated_at as "Última Atualização"
FROM
  github_repository
WHERE
  owner_login = (SELECT login FROM github_organization LIMIT 1)
  AND open_issues_count > 50
  AND NOT is_archived
ORDER BY
  open_issues_count DESC;

-- 2. Repositórios com mais Stars
-- Identifica projetos mais populares
SELECT
  name as "Repositório",
  stargazers_count as "Stars",
  forks_count as "Forks",
  watchers_count as "Watchers",
  visibility as "Visibilidade",
  description as "Descrição"
FROM
  github_repository
WHERE
  owner_login = (SELECT login FROM github_organization LIMIT 1)
  AND NOT is_archived
ORDER BY
  stargazers_count DESC
LIMIT 20;

-- 3. Commits Recentes por Autor
-- Vê atividade dos desenvolvedores
SELECT
  author_login as "Desenvolvedor",
  COUNT(*) as "Commits (últimos 30 dias)",
  MIN(author_date) as "Primeiro Commit",
  MAX(author_date) as "Último Commit"
FROM
  github_commit
WHERE
  author_date > NOW() - INTERVAL '30 days'
GROUP BY
  author_login
ORDER BY
  COUNT(*) DESC;

-- 4. Repositórios por Linguagem
-- Distribuição de tecnologias
SELECT
  language as "Linguagem",
  COUNT(*) as "Número de Repositórios",
  ROUND(AVG(size)::numeric, 2) as "Tamanho Médio (KB)"
FROM
  github_repository
WHERE
  owner_login = (SELECT login FROM github_organization LIMIT 1)
  AND language IS NOT NULL
  AND NOT is_archived
GROUP BY
  language
ORDER BY
  COUNT(*) DESC;

-- 5. Pull Requests Abertas há Muito Tempo
-- PRs que podem estar travadas
SELECT
  repository_full_name as "Repositório",
  number as "PR #",
  title as "Título",
  user_login as "Autor",
  created_at as "Criada em",
  DATE_PART('day', NOW() - created_at) as "Dias Aberta",
  state as "Estado"
FROM
  github_pull_request
WHERE
  repository_full_name LIKE (SELECT login FROM github_organization LIMIT 1) || '%'
  AND state = 'open'
  AND created_at < NOW() - INTERVAL '30 days'
ORDER BY
  created_at ASC;

-- 6. Repositórios com Vulnerability Alerts
-- Repos com vulnerabilidades conhecidas
SELECT
  r.name as "Repositório",
  r.visibility as "Visibilidade",
  r.has_vulnerability_alerts_enabled as "Alerts Habilitados",
  r.pushed_at as "Último Push"
FROM
  github_repository r
WHERE
  r.owner_login = (SELECT login FROM github_organization LIMIT 1)
  AND NOT r.is_archived
  AND r.has_vulnerability_alerts_enabled = true
ORDER BY
  r.name;

-- 7. Times com Mais Membros
-- Estrutura organizacional
SELECT
  name as "Time",
  slug as "Slug",
  members_count as "Membros",
  repos_count as "Repositórios",
  privacy as "Privacidade",
  description as "Descrição"
FROM
  github_team
WHERE
  organization = (SELECT login FROM github_organization LIMIT 1)
ORDER BY
  members_count DESC;

-- 8. Repositórios Criados Recentemente
-- Novos projetos (últimos 90 dias)
SELECT
  name as "Novo Repositório",
  visibility as "Visibilidade",
  created_at as "Criado em",
  description as "Descrição",
  default_branch as "Branch Padrão",
  CASE
    WHEN EXISTS (
      SELECT 1 FROM github_branch b
      WHERE b.repository_full_name = r.full_name
      AND b.name = r.default_branch
      AND b.protected = true
    )
    THEN 'SIM'
    ELSE 'NÃO'
  END as "Branch Protegida"
FROM
  github_repository r
WHERE
  r.owner_login = (SELECT login FROM github_organization LIMIT 1)
  AND r.created_at > NOW() - INTERVAL '90 days'
ORDER BY
  r.created_at DESC;

-- 9. Colaboradores com Mais Commits
-- Top contributors
SELECT
  c.author_login as "Colaborador",
  COUNT(DISTINCT c.repository_full_name) as "Repositórios",
  COUNT(*) as "Total de Commits",
  MIN(c.author_date) as "Primeiro Commit",
  MAX(c.author_date) as "Último Commit"
FROM
  github_commit c
WHERE
  c.repository_full_name LIKE (SELECT login FROM github_organization LIMIT 1) || '%'
  AND c.author_date > NOW() - INTERVAL '1 year'
GROUP BY
  c.author_login
ORDER BY
  COUNT(*) DESC
LIMIT 20;

-- 10. Repositórios sem Tags/Releases
-- Projetos que podem precisar de versionamento
SELECT
  name as "Repositório",
  visibility as "Visibilidade",
  created_at as "Criado em",
  pushed_at as "Último Push",
  description as "Descrição"
FROM
  github_repository
WHERE
  owner_login = (SELECT login FROM github_organization LIMIT 1)
  AND NOT is_archived
  AND NOT EXISTS (
    SELECT 1 FROM github_tag
    WHERE repository_full_name = github_repository.full_name
  )
ORDER BY
  created_at DESC;

-- 11. Webhooks por Repositório
-- Auditoria de webhooks configurados
SELECT
  w.repository_name as "Repositório",
  w.config ->> 'url' as "URL do Webhook",
  w.active as "Ativo",
  w.events as "Eventos",
  w.created_at as "Criado em"
FROM
  github_repository_webhook w
  JOIN github_repository r ON w.repository_name = r.name
WHERE
  r.owner_login = (SELECT login FROM github_organization LIMIT 1)
ORDER BY
  w.repository_name, w.created_at;

-- 12. Configurações de Merge para PRs
-- Como PRs são mescladas
SELECT
  name as "Repositório",
  visibility as "Visibilidade",
  allow_merge_commit as "Permite Merge Commit",
  allow_squash_merge as "Permite Squash",
  allow_rebase_merge as "Permite Rebase",
  delete_branch_on_merge as "Deleta Branch ao Merge"
FROM
  github_repository
WHERE
  owner_login = (SELECT login FROM github_organization LIMIT 1)
  AND NOT is_archived
ORDER BY
  name;

-- 13. Usuários que Entraram Recentemente
-- Novos membros (últimos 90 dias)
SELECT
  login as "Novo Membro",
  name as "Nome Completo",
  email as "Email",
  role as "Função",
  two_factor_disabled as "2FA Desabilitado",
  created_at as "Membro Desde"
FROM
  github_organization_member
WHERE
  organization = (SELECT login FROM github_organization LIMIT 1)
  AND created_at > NOW() - INTERVAL '90 days'
ORDER BY
  created_at DESC;

-- 14. Actions/Workflows Configuradas
-- Auditoria de workflows de CI/CD
SELECT
  repository_full_name as "Repositório",
  name as "Workflow",
  path as "Caminho",
  state as "Estado"
FROM
  github_workflow
WHERE
  repository_full_name LIKE (SELECT login FROM github_organization LIMIT 1) || '%'
ORDER BY
  repository_full_name, name;

-- 15. Compliance Score Simplificado
-- Score básico de compliance por repositório
SELECT
  name as "Repositório",
  visibility as "Visibilidade",
  -- Branch Protection (25 pontos)
  CASE
    WHEN EXISTS (
      SELECT 1 FROM github_branch b
      WHERE b.repository_full_name = r.full_name
      AND b.name = r.default_branch
      AND b.protected = true
    )
    THEN 25
    ELSE 0
  END as "Branch Protection (25)",
  -- Secret Scanning (25 pontos)
  CASE
    WHEN COALESCE(
      security_and_analysis -> 'secret_scanning' ->> 'status',
      'disabled'
    ) = 'enabled'
    THEN 25
    ELSE 0
  END as "Secret Scanning (25)",
  -- Dependabot (25 pontos)
  CASE
    WHEN COALESCE(
      security_and_analysis -> 'dependabot_security_updates' ->> 'status',
      'disabled'
    ) = 'enabled'
    THEN 25
    ELSE 0
  END as "Dependabot (25)",
  -- Licença (25 pontos)
  CASE
    WHEN license_info IS NOT NULL
    THEN 25
    ELSE 0
  END as "Licença (25)",
  -- Score Total
  (
    CASE WHEN EXISTS (SELECT 1 FROM github_branch b WHERE b.repository_full_name = r.full_name AND b.name = r.default_branch AND b.protected = true) THEN 25 ELSE 0 END +
    CASE WHEN COALESCE(security_and_analysis -> 'secret_scanning' ->> 'status', 'disabled') = 'enabled' THEN 25 ELSE 0 END +
    CASE WHEN COALESCE(security_and_analysis -> 'dependabot_security_updates' ->> 'status', 'disabled') = 'enabled' THEN 25 ELSE 0 END +
    CASE WHEN license_info IS NOT NULL THEN 25 ELSE 0 END
  ) as "Score Total (/100)"
FROM
  github_repository r
WHERE
  r.owner_login = (SELECT login FROM github_organization LIMIT 1)
  AND NOT r.is_archived
ORDER BY
  "Score Total (/100)" ASC, r.name;
