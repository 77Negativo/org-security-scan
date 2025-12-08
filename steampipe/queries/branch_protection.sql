-- Branch protection status para repositórios
-- Nota: Simplificado devido a limitações de permissões do token
-- Esta query retorna dados limitados - para informações completas de branch protection,
-- são necessárias permissões adicionais no token
SELECT
  name_with_owner as repository,
  name as repo_name,
  visibility,
  created_at
FROM
  github_my_repository
ORDER BY name_with_owner
LIMIT 100;
