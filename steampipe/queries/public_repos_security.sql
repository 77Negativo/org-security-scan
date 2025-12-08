-- Auditoria de Segurança de Repositórios Públicos
-- Foca em repositórios públicos que precisam de atenção especial
SELECT
  name,
  name_with_owner as full_name,
  visibility,
  created_at,
  updated_at,
  CASE
    WHEN visibility = 'PUBLIC' THEN 'CRITICAL'
    ELSE 'LOW'
  END as security_priority
FROM
  github_my_repository
WHERE
  visibility = 'PUBLIC'
ORDER BY
  updated_at DESC
LIMIT 50;
