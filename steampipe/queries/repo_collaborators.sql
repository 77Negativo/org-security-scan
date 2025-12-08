-- Auditoria de colaboradores de repositórios
-- Lista todos os colaboradores com suas permissões em cada repo
SELECT
  r.name_with_owner as repository,
  r.visibility,
  c.user_login as collaborator,
  c.permission,
  c.affiliation
FROM
  github_my_repository r
  LEFT JOIN github_repository_collaborator c ON r.name_with_owner = c.repository_full_name
WHERE
  c.user_login IS NOT NULL
ORDER BY
  r.name_with_owner,
  c.permission DESC,
  c.affiliation
LIMIT 500;
