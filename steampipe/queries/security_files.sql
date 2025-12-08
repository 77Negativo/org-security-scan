-- Verificação de arquivos de segurança (SECURITY.md, CODE_OF_CONDUCT.md, etc)
-- Lista repositórios e indica quais têm arquivos de segurança
SELECT
  r.name_with_owner as repository,
  r.name as repo_name,
  r.visibility,
  r.created_at,
  r.updated_at
FROM
  github_my_repository r
ORDER BY
  r.visibility DESC,
  r.updated_at DESC
LIMIT 100;
