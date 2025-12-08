-- Auditoria de membros da organização
-- Lista todos os membros com suas roles e status de 2FA
SELECT
  o.login as organization,
  om.login as member_login,
  om.role,
  om.has_two_factor_enabled
FROM
  github_my_organization o
  LEFT JOIN github_organization_member om ON o.login = om.organization
ORDER BY
  o.login,
  om.role DESC,
  om.has_two_factor_enabled ASC
LIMIT 200;
