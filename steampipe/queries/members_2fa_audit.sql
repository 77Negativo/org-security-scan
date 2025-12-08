-- Auditoria Detalhada de 2FA dos Membros da Organização
-- Lista todos os membros com foco em compliance de 2FA
SELECT
  o.login as organization,
  om.login as member_login,
  om.role,
  om.has_two_factor_enabled as two_factor_enabled,
  CASE
    WHEN om.has_two_factor_enabled = false AND om.role = 'ADMIN' THEN 'CRITICAL'
    WHEN om.has_two_factor_enabled = false THEN 'HIGH'
    ELSE 'OK'
  END as security_risk_level
FROM
  github_my_organization o
  LEFT JOIN github_organization_member om ON o.login = om.organization
WHERE
  om.login IS NOT NULL
ORDER BY
  om.has_two_factor_enabled ASC,
  om.role DESC
LIMIT 200;
