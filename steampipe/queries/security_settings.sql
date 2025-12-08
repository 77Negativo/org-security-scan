-- Configurações de segurança (detecta automaticamente via token)
SELECT
  name as "Repositório",
  visibility as "Visibilidade",
  created_at as "Criado Em",
  updated_at as "Atualizado Em"
FROM
  github_my_repository
WHERE
  name_with_owner LIKE (SELECT login FROM github_my_organization LIMIT 1) || '/%'
ORDER BY
  updated_at DESC
LIMIT 100;
