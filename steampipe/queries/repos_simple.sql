-- Visão geral simplificada de repositórios
SELECT
  name,
  visibility,
  is_archived,
  default_branch,
  open_issues_count,
  pushed_at,
  CASE
    WHEN pushed_at < NOW() - INTERVAL '6 months' THEN 'inactive'
    ELSE 'active'
  END as activity_status
FROM
  github_repository
WHERE
  owner_login = (SELECT login FROM github_organization LIMIT 1)
ORDER BY
  pushed_at DESC;
