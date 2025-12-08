# 🔐 GitHub Organization Security Scanner

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-blue)](https://github.com/features/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**Automated security auditing for GitHub organizations using native GitHub REST API.**

A lightweight, zero-dependency tool that continuously monitors your GitHub organization's security posture, generating comprehensive reports and interactive dashboards.

## ✨ Features

- 🚀 **Zero External Dependencies** - Uses only GitHub REST API (no Steampipe, PostgreSQL, or other tools)
- ⚡ **Fast Execution** - Complete audit in ~1-2 minutes
- 🤖 **Fully Automated** - Runs weekly via GitHub Actions + manual trigger
- 📊 **Interactive Dashboard** - Beautiful HTML reports with insights
- 🔍 **Comprehensive Audits** - Repositories, users, permissions, branch protection, security settings
- 🎯 **Auto-Detection** - Automatically detects your organization
- ⚠️ **Issue Creation** - Automatically creates GitHub issues for critical findings
- 📈 **Historical Tracking** - All reports stored in git for trend analysis

## 🚀 Quick Start

### Prerequisites

- GitHub organization (or personal account)
- GitHub token with these scopes:
  - `repo` - Repository access
  - `read:org` - Organization read access
  - `read:user` - User profile read access

### Installation

**1. Use This Template or Fork**

Click "Use this template" or fork this repository to your organization.

**2. Create GitHub Token**

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `read:org`, `read:user`
4. Copy the token

**3. Add Secret to Repository**

1. Go to your repository settings
2. Navigate to: `Settings` → `Secrets and variables` → `Actions`
3. Click "New repository secret"
4. Name: `ORG_SECURITY_TOKEN`
5. Value: Paste your token
6. Click "Add secret"

**4. Enable Workflow Permissions**

1. Go to `Settings` → `Actions` → `General`
2. Under "Workflow permissions", select "Read and write permissions"
3. Click "Save"

**5. Run!**

Go to `Actions` → `Organization Security Scan` → `Run workflow`

That's it! 🎉

## 📊 What Gets Audited

### 🗂️ Repositories
- Total repositories (public/private)
- Repositories without descriptions
- Inactive repositories (>6 months)
- Repositories without licenses
- Repository visibility settings

### 🛡️ Branch Protection
- Repositories with/without branch protection
- Protection rule details
- Unprotected critical branches

### 👥 Users & Permissions
- Organization members
- External collaborators
- Team memberships
- Members without 2FA (when available)
- Inactive collaborators

### 🔒 Security Settings
- Secret scanning status
- Dependabot configuration
- Security policy files (SECURITY.md)
- Security advisories

## 📁 Project Structure

```
org-security-scan/
├── .github/
│   ├── workflows/
│   │   └── org-security-scan.yml    # Main workflow
│   └── SECURITY.md                  # Security policy
├── scripts/
│   ├── github_api_audit.py          # Main audit script (REST API)
│   ├── generate_dashboard.py        # Dashboard generator
│   ├── check_security_files.py      # Security files checker
│   ├── check_inactive_collaborators.py  # Inactive users checker
│   ├── create_issue.py              # Issue creator
│   └── test_local_native.sh         # Local testing script
├── reports/                         # Generated reports (gitignored)
│   ├── audit_results_*.json         # Raw audit data
│   └── security_dashboard_*.html    # Interactive dashboard
├── MIGRATION_GUIDE.md               # For Steampipe users
├── INSTALL.md                       # Detailed installation
├── QUICKSTART.md                    # Quick start guide
├── SETUP_CHECKLIST.md               # Setup checklist
└── README.md                        # This file
```

## 🔧 Configuration

### Environment Variables

The scripts support multiple token environment variable names:

```bash
# In order of precedence:
GH_TOKEN=your_token              # Recommended
ORG_SECURITY_TOKEN=your_token    # GitHub Actions default
GITHUB_TOKEN=your_token          # Fallback
```

### Workflow Schedule

By default, runs weekly on Mondays at 9 AM UTC. Customize in `.github/workflows/org-security-scan.yml`:

```yaml
on:
  schedule:
    - cron: '0 9 * * 1'  # Customize this
```

## 💻 Local Testing

Test locally before pushing to GitHub:

```bash
# 1. Set your token
export GH_TOKEN='your_github_token_here'

# 2. Run the test script
./scripts/test_local_native.sh

# 3. View results
open reports/security_dashboard_latest.html
```

**Requirements:**
- Python 3.11+
- `requests` library: `pip install requests`

## 📖 Documentation

- **[Installation Guide](INSTALL.md)** - Detailed setup instructions
- **[Quick Start Guide](QUICKSTART.md)** - Get started in 5 minutes
- **[Setup Checklist](SETUP_CHECKLIST.md)** - Step-by-step checklist
- **[Migration Guide](MIGRATION_GUIDE.md)** - Migrating from Steampipe
- **[Security Policy](.github/SECURITY.md)** - Security guidelines

## 🔍 Example Reports

The workflow generates:

1. **JSON Reports** (`audit_results_*.json`)
   - Complete audit data
   - Machine-readable format
   - Historical comparison

2. **HTML Dashboard** (`security_dashboard_*.html`)
   - Interactive web interface
   - Visual charts and graphs
   - Executive summary
   - Actionable recommendations

3. **GitHub Issues** (optional)
   - Created for critical findings
   - Tagged with severity levels
   - Action items included

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development

```bash
# Clone the repository
git clone https://github.com/your-org/org-security-scan.git
cd org-security-scan

# Test locally
export GH_TOKEN='your_token'
./scripts/test_local_native.sh

# Make changes and test
python3 scripts/github_api_audit.py
```

## 🆚 Why This Tool?

| Feature | This Tool | Steampipe-based | Other Tools |
|---------|-----------|-----------------|-------------|
| Installation | ✅ None | ❌ Complex | ⚠️ Varies |
| Dependencies | ✅ Python + requests | ❌ PostgreSQL + plugins | ⚠️ Many |
| Speed | ✅ 1-2 min | ⚠️ 5-8 min | ⚠️ Varies |
| Portability | ✅ Runs anywhere | ❌ Linux/Mac only | ⚠️ Varies |
| Maintenance | ✅ Low | ⚠️ High | ⚠️ Varies |

## 📋 Roadmap

- [ ] Support for GitHub Enterprise Server
- [ ] Slack/Discord notifications
- [ ] Custom compliance rules
- [ ] Multi-organization support
- [ ] Trend analysis and charts
- [ ] PDF report generation

## 🐛 Troubleshooting

### "No module named 'requests'"
```bash
pip install requests
```

### "Token not found"
```bash
export GH_TOKEN='your_token_here'
```

### "Permission denied"
Make sure your token has the correct scopes: `repo`, `read:org`, `read:user`

### Rate Limiting
The tool respects GitHub API rate limits (5,000 requests/hour for authenticated users). If you hit the limit, wait an hour or reduce the scope of auditing.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [GitHub REST API](https://docs.github.com/en/rest)
- Inspired by security best practices from the GitHub Security Lab
- Community contributions and feedback

## 📧 Support

- 📖 [Documentation](./INSTALL.md)
- 🐛 [Report Issues](https://github.com/77Negativo/org-security-scan/issues)
- 💬 [Discussions](https://github.com/77Negativo/org-security-scan/discussions)

---

**Made with ❤️ by the community. Star ⭐ this repo if you find it useful!**
