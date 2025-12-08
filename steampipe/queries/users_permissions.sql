-- Organizações que o token tem acesso
SELECT
  login,
  name,
  created_at,
  updated_at
FROM
  github_my_organization
LIMIT 10;
