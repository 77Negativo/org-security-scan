-- Status de Dependabot e alertas de vulnerabilidade por repositório
SELECT
  name,
  name_with_owner as full_name,
  visibility,
  created_at,
  updated_at
FROM
  github_my_repository
ORDER BY
  updated_at DESC
LIMIT 100;
