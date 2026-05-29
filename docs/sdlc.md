# SDLC Workflow for Solo Multi-Repo Development

**Project**: DevOps/LLMOps toolchain  
**Issue**: HAP-96  
**Status**: Draft  
**Last Updated**: 2026-05-29

---

## 1. Overview

This document defines the Software Development Lifecycle (SDLC) workflow for solo multi-repository development across the Hyperview ecosystem, specifically for the `workout_backend` (Elixir/Phoenix) and `workout_frontend` (React Native/Expo) repositories.

### 1.1 Scope
- **workout_backend**: `/Users/regismartin/dev/hyperview/hyperview/workout_backend`
- **workout_frontend**: `/Users/regismartin/dev/hyperview/hyperview/workout_frontend`
- **This repo (devops)**: Shared documentation and tooling

### 1.2 Principles
- **Consistency**: Same workflow across all repos
- **Traceability**: All changes linked to Linear issues (HAP-*)
- **Safety**: Automated validation before production
- **Reproducibility**: Clear rollback procedures

---

## 2. Branch Strategy

### 2.1 Branch Types

| Branch Type | Naming Convention | Purpose | Lifetime |
|-------------|------------------|---------|----------|
| main | `main` | Production-ready code | Permanent |
| develop | `develop` | Integration/staging | Permanent |
| feature | `feature/HAP-{n}-{slug}` | New functionality | Short-lived |
| hotfix | `hotfix/HAP-{n}-{description}` | Critical bug fixes | Short-lived |
| release | `release/v{MAJOR}.{MINOR}` | Release preparation | Short-lived |

### 2.2 Branch Creation Rules

**Feature Branches**:
```bash
# From main (preferred for isolated features)
git checkout main
git pull origin main
git checkout -b feature/HAP-96-sdlc-workflow

# From develop (for features depending on other work)
git checkout develop
git pull origin develop
git checkout -b feature/HAP-99-cool-feature
```

**Hotfix Branches** (always from main):
```bash
git checkout main
git pull origin main
git checkout -b hotfix/HAP-100-critical-bug
```

### 2.3 Branch Synchronization (Multi-Repo)

When working on features that span both repos:

1. **Create feature branches with same name in both repos**
   ```bash
   # In workout_backend
   git checkout -b feature/HAP-96-sdlc-workflow
   
   # In workout_frontend  
   git checkout -b feature/HAP-96-sdlc-workflow
   ```

2. **Use a shared prefix** for coordinated work:
   - `feature/HAP-{n}-` for issue-specific work
   - `sync/` for cross-repo synchronization

3. **Document dependencies** in PR descriptions:
   ```markdown
   **Depends on**: workout_backend#feature/HAP-96-sdlc-workflow
   **Blocks**: workout_frontend#feature/HAP-97-frontend-integration
   ```

---

## 3. PR Rules

### 3.1 PR Requirements

**Mandatory for all PRs:**
- [ ] Linked to Linear issue (HAP-*)
- [ ] Descriptive title (use issue title or summarize change)
- [ ] PR template completed (see Section 3.2)
- [ ] All CI checks passing
- [ ] Self-review completed

### 3.2 PR Template

```markdown
## Description

Closes HAP-{n}

{Brief description of changes}

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation
- [ ] Refactor
- [ ] Test
- [ ] Chore

## Affected Repos
- [ ] workout_backend
- [ ] workout_frontend
- [ ] devops

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Commit messages are descriptive
- [ ] Documentation updated
- [ ] No sensitive data exposed

## Dependencies
- **Depends on**: {list PRs or commits}
- **Blocks**: {list issues or PRs}

## Screenshots/Videos (if UI changes)
```

### 3.3 PR Review Process (Solo Development)

Since this is primarily solo development:

1. **Self-Review First**
   - Review own code after 24 hours (fresh perspective)
   - Run through the PR checklist
   - Verify all tests pass

2. **Optional External Review**
   - Tag `@regismartin` for critical changes
   - Use GitHub/GitLab review requests
   - Aim for 1 approval minimum

3. **Merge Strategy**
   - **Preferred**: Squash and merge (keeps history clean)
   - **Alternative**: Rebase and merge (preserves commit history)
   - **Avoid**: Merge commits (creates unnecessary noise)

### 3.4 PR Naming Convention

```
HAP-{n}: {short description}
```

Examples:
- `HAP-96: Add SDLC workflow documentation`
- `HAP-97: Implement coach personality evaluation`
- `fix: Resolve build error in CI`

---

## 4. Commit Habits

### 4.1 Commit Message Format

**Structure**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**For Linear issues**:
```
HAP-{n}: <imperative verb> <description>

<detailed explanation if needed>

Closes HAP-{n}
```

### 4.2 Commit Types

| Type | When to Use | Example |
|------|-------------|---------|
| feat | New feature | `HAP-96: Add branch strategy documentation` |
| fix | Bug fix | `HAP-100: Fix null pointer in coach harness` |
| docs | Documentation only | `docs: Update README with setup instructions` |
| style | Formatting, missing semicolons | `style: Format code with prettier` |
| refactor | Code refactor (no functional changes) | `refactor: Extract coach personality logic` |
| test | Adding tests | `test: Add unit tests for eval runner` |
| chore | Build process, dependencies | `chore: Update Elixir to 1.16` |

### 4.3 Commit Best Practices

**DO:**
- Use imperative mood: "Add feature" not "Added feature"
- Keep subject line under 72 characters
- Reference Linear issue in first line
- Separate subject from body with blank line
- Wrap body at 72 characters
- Use bullet points for multiple changes

**DON'T:**
- Use past tense
- Include unnecessary details in subject
- Mix multiple unrelated changes
- Use vague messages like "fix stuff"

### 4.4 Atomic Commits

Each commit should be:
- **Single logical change**: One feature, one bug fix, one refactor
- **Self-contained**: Can be applied independently
- **Testable**: Passes all tests on its own
- **Reversible**: Can be reverted without breaking other changes

### 4.5 Commit Signing (Recommended)

```bash
# Set up GPG signing
git config --global user.signingkey <your-gpg-key>
git config --global commit.gpgsign true

# Or use SSH signing
git config --global gpg.format ssh
git config --global user.signingkey /path/to/ssh/key.pub
```

---

## 5. Release Cadence

### 5.1 Versioning

**Semantic Versioning (SemVer 2.0.0)**:
```
MAJOR.MINOR.PATCH
```

- **MAJOR**: Breaking changes, significant new features
- **MINOR**: Backwards-compatible new features
- **PATCH**: Backwards-compatible bug fixes

### 5.2 Release Schedule

| Release Type | Frequency | Day/Time | Trigger |
|--------------|-----------|----------|---------|
| Patch | As needed | Any | Critical bug fix |
| Minor | Weekly | Friday 14:00 CET | Accumulated features |
| Major | Quarterly | End of quarter | Significant changes |

### 5.3 Release Process

**For Minor Releases (Weekly):**

1. **Thursday**
   - Review all merged features
   - Update CHANGELOG.md
   - Create release branch: `release/v1.x.0`

2. **Friday 10:00**
   - Run full test suite
   - Manual QA on staging
   - Final review of CHANGELOG

3. **Friday 14:00**
   - Tag release: `v1.x.0`
   - Push to main
   - Deploy to production
   - Announce in #releases

### 5.4 Changelog Format

```markdown
# Changelog

## [v1.2.0] - 2026-05-30

### Added
- HAP-96: SDLC workflow documentation
- HAP-97: Coach personality evaluation system

### Changed
- Updated dependency versions

### Fixed
- HAP-100: Null pointer in coach harness

### Removed
- Legacy API endpoints
```

### 5.5 Version Files

- **workout_backend**: `mix.exs` (Elixir version)
- **workout_frontend**: `package.json` (version field)
- **Changelog**: `CHANGELOG.md` in each repo

---

## 6. QA Promotion

### 6.1 Environments

| Environment | Branch | Purpose | URL |
|-------------|--------|---------|-----|
| Local | Any | Development | localhost |
| Staging | develop | Integration testing | staging.hyperview.ai |
| Production | main | Live | hyperview.ai |

### 6.2 Staging Deployment

**Automatic** (on PR merge to develop):
1. CircleCI runs backend tests
2. Backend deploys to staging
3. Frontend builds and deploys to staging
4. Automated smoke tests run

**Manual Verification Checklist**:
- [ ] All API endpoints respond
- [ ] Frontend loads without errors
- [ ] Key user journeys work
- [ ] No console errors
- [ ] Mobile responsive design OK

### 6.3 QA Gates

**Must Pass Before Production:**
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Linting passes
- [ ] Build succeeds
- [ ] Staging smoke tests pass
- [ ] Manual QA checklist completed

### 6.4 Automated Testing

**workout_backend**:
```bash
# Run all tests
mix test

# Run specific test
mix test test/workout_backend/some_test.exs

# Lint
mix credo
mix dialyzer
```

**workout_frontend**:
```bash
# Run tests
npm test

# Lint
npm run lint

# Type check
npm run type-check
```

---

## 7. Production Promotion

### 7.1 Deployment Process

**Manual Deployment (from main branch):**

1. **Pre-deployment**:
   ```bash
   # Verify main branch is clean
   git checkout main
   git pull origin main
   git status
   ```

2. **Tag Release**:
   ```bash
   git tag -a v1.2.0 -m "Release v1.2.0"
   git push origin v1.2.0
   ```

3. **Deploy Backend**:
   ```bash
   # Using Docker
   docker-compose -f docker-compose.prod.yml build
   docker-compose -f docker-compose.prod.yml up -d
   
   # Or using Gigalixir/Heroku
   gigalixir ps:restart
   ```

4. **Deploy Frontend**:
   ```bash
   # Build
   expo build:android
   expo build:ios
   
   # Or using EAS
   eas build --platform all
   eas submit -p android
   eas submit -p ios
   ```

5. **Verify Deployment**:
   - Health check endpoint: `GET /health`
   - Frontend: Load app, test key flows
   - Database: Verify migrations applied

### 7.2 Deployment Windows

- **Regular**: Friday 14:00-15:00 CET
- **Emergency**: Any time (hotfix process)
- **Maintenance**: Announced in #general 48 hours prior

### 7.3 Communication

**Before Deployment**:
- Announce in #releases: "Deploying v1.2.0 in 30 minutes"

**After Deployment**:
- Announce in #releases: "v1.2.0 deployed successfully"
- Include: Version, timestamp, key changes

---

## 8. Rollback Procedures

### 8.1 When to Rollback

- Critical bug in production
- Data corruption risk
- Performance degradation >50%
- Security vulnerability
- Failed health checks

### 8.2 Rollback Methods

**Method 1: Git Revert (Code changes)**
```bash
# Identify bad commit
git log --oneline main | head -20

# Revert specific commit
git revert <bad-commit-hash>
git push origin main

# Re-deploy
git checkout main
git pull origin main
# Trigger deployment
```

**Method 2: Rollback to Previous Tag**
```bash
# Checkout previous stable version
git checkout v1.1.0

# Re-deploy
# ... deployment commands
```

**Method 3: Database Rollback**
```bash
# For Ecto migrations
mix ecto.rollback -n 1

# Check migration status
mix ecto.psql -c "SELECT * FROM schema_migrations;"
```

### 8.3 Rollback Communication

**Immediate (within 5 minutes)**:
- Slack: `#incidents` channel
- Message: "ROLLBACK INITIATED: v1.2.0 due to {reason}. Rolling back to v1.1.0"

**Post-Rollback (within 1 hour)**:
- Post-mortem in #incidents
- Linear issue created for root cause
- Customer communication if affected

### 8.4 Rollback Window

- **Hotfix**: 1 hour
- **Regular release**: 4 hours
- **Major release**: 24 hours

---

## 9. Repository-Specific Guidelines

### 9.1 workout_backend (Elixir/Phoenix)

**Tech Stack**:
- Language: Elixir 1.16+
- Framework: Phoenix 1.7+
- Database: PostgreSQL 15+
- Cache: Redis
- Testing: ExUnit, Wallaby

**Dependencies**:
```elixir
# mix.exs
defp deps do [
  {:phoenix, "~> 1.7"},
  {:ecto_sql, "~> 3.10"},
  {:postgrex, ">= 0.0.0"},
  # ...
]
end
```

**Development**:
```bash
# Start server
mix phx.server

# Run tests
mix test

# Database setup
mix ecto.create
mix ecto.migrate
mix ecto.seed
```

### 9.2 workout_frontend (React Native/Expo)

**Tech Stack**:
- Framework: Expo SDK 50+
- Language: TypeScript
- UI: React Native, Native Base
- Navigation: React Navigation
- Testing: Jest, React Native Testing Library

**Dependencies**:
```json
{
  "dependencies": {
    "expo": "^50.0.0",
    "react": "18.2.0",
    "react-native": "0.73.0",
    "@react-navigation/native": "^6.1.0"
  }
}
```

**Development**:
```bash
# Start development server
npx expo start

# Run on device
npx expo start --ios
npx expo start --android

# Build for production
expo build:android
expo build:ios
```

---

## 10. Multi-Repo Coordination

### 10.1 Cross-Repo Changes

When changes affect both repos:

1. **Create synchronized branches**
2. **Document in both PRs**
3. **Merge backend first** (if frontend depends on it)
4. **Update frontend** with new API contracts
5. **Deploy backend, then frontend**

### 10.2 API Contract Changes

**Breaking Changes**:
- Bump MAJOR version
- Announce in #backend 1 week before
- Provide migration guide

**Non-Breaking Changes**:
- Bump MINOR version
- Update OpenAPI/Swagger docs
- Update frontend type definitions

### 10.3 Shared Configuration

Store shared configs in this repo (`devops/`):
```
devops/
├── config/
│   ├── shared.env          # Shared environment variables
│   ├── api-contracts.yml    # API endpoint definitions
│   └── feature-flags.yml     # Feature flag configurations
├── scripts/
│   ├── deploy-backend.sh
│   ├── deploy-frontend.sh
│   └── rollback.sh
└── docs/
    └── sdlc.md              # This document
```

---

## 11. Tooling & Automation

### 11.1 CI/CD

#### Option A: CircleCI (Current Setup)

**workout_backend**:
- Location: `.circleci/config.yml`
- Triggers: On PR and push to main/develop
- Jobs: Test, lint, build, security scan

#### Option B: GitHub Actions (Recommended for Solo Devs)

**Why GitHub Actions for Solo Development:**
- ✅ Zero additional accounts/services to manage
- ✅ Native GitHub integration
- ✅ Generous free tier (2000 minutes/month)
- ✅ Configuration lives in your repo (`.github/workflows/`)
- ✅ Easy to customize and extend

**workout_backend (.github/workflows/test-backend.yml)**:
```yaml
name: Backend Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: workout_backend_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Elixir
        uses: actions/setup-elixir@v1
        with:
          elixir-version: 1.16
          otp-version: 26
          
      - name: Install dependencies
        run: |
          mix local.rebar --force
          mix local.hex --force
          mix deps.get
      
      - name: Compile
        run: mix compile --warnings-as-errors
      
      - name: Run tests
        run: mix test
        env:
          MIX_ENV: test
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/workout_backend_test
      
      - name: Lint
        run: |
          mix credo --strict
          mix dialyzer
```

**workout_frontend (.github/workflows/test-frontend.yml)**:
```yaml
name: Frontend Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      
      - name: Install dependencies
        run: npm ci
      
      - name: Type check
        run: npm run type-check
      
      - name: Lint
        run: npm run lint
      
      - name: Run tests
        run: npm test
```

**Combined Workflow (both repos in one file)**:
```yaml
name: Full Stack Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        ports: ["5432:5432"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-elixir@v1
        with:
          elixir-version: 1.16
          otp-version: 26
      - run: mix deps.get && mix test

  frontend:
    needs: backend
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci && npm test
```

#### Option C: Local Scripts (Simplest for Solo)

If you prefer no cloud CI at all, use a `Makefile`:

**workout_backend/Makefile**:
```makefile
.PHONY: test lint setup

setup: deps database

deps:
	mix deps.get

database:
	mix ecto.create
	mix ecto.migrate

test: deps
	mix test

lint: deps
	mix credo --strict
	dialyzer

all: setup test lint
```

**workout_frontend/package.json scripts**:
```json
{
  "scripts": {
    "test": "jest",
    "lint": "eslint .",
    "type-check": "tsc --noEmit",
    "ci": "npm ci",
    "validate": "npm run lint && npm run type-check && npm test"
  }
}
```

Run locally: `make test` or `npm run validate`

### 11.2 Local Development Tools

| Tool | Purpose | Config File |
|------|---------|-------------|
| asdf | Version management | `.tool-versions` |
| Docker | Containerization | `Dockerfile`, `docker-compose.yml` |
| Git Hooks | Pre-commit checks | `.git/hooks/` |
| EditorConfig | Code style | `.editorconfig` |
| ESLint | JS linting | `.eslintrc` |
| Credo | Elixir linting | `.cred.exs` |

### 11.3 Monitoring

**Backend**:
- Logging: Logger (Elixir)
- Metrics: Telemetry + Prometheus
- APM: AppSignal/Sentry

**Frontend**:
- Error tracking: Sentry
- Analytics: Mixpanel/Amplitude
- Performance: React Native Debugger

---

## 12. Security

### 12.1 Secrets Management

**Never commit secrets to Git.**

Use environment variables:
```bash
# .env file (in .gitignore)
DATABASE_URL=postgres://user:pass@localhost/db
API_KEY=secret_key_here
```

**Production**:
- Use Vault/Secrets Manager
- Rotate secrets quarterly
- Never log secrets

### 12.2 Dependency Security

```bash
# Backend
mix deps.audit

# Frontend
npm audit
npx expo-doctor
```

### 12.3 Code Review Security Checklist

- [ ] No hardcoded credentials
- [ ] No API keys in client-side code
- [ ] Input validation present
- [ ] SQL injection prevention (Ecto parameterized queries)
- [ ] XSS prevention (HTML escaping)
- [ ] Rate limiting on public endpoints
- [ ] Authentication/authorization checks

---

## 13. Maintenance

### 13.1 Regular Tasks

| Task | Frequency | Owner |
|------|-----------|-------|
| Dependency updates | Weekly | Developer |
| Security audit | Monthly | Developer |
| Database backup | Daily (automated) | System |
| Log rotation | Daily (automated) | System |
| Performance review | Quarterly | Developer |

### 13.2 Documentation Updates

- Update this document when workflow changes
- Keep CHANGELOG.md current
- Update README files with setup instructions
- Document breaking changes in migration guides

---

## 14. Contacts & Escalation

| Issue Type | Contact | Escalation |
|------------|---------|------------|
| Development questions | @regismartin | #devops |
| Production incidents | @regismartin | #incidents |
| Security concerns | @regismartin | #security |
| Feature requests | Linear | #product |

**Emergency Contact**: régis.martinravel@gmail.com

---

## Appendix A: Quick Reference Commands

### Git Commands
```bash
# Start new feature
git checkout main
git pull origin main
git checkout -b feature/HAP-96-feature-name

# Commit changes
git add .
git commit -m "HAP-96: Add feature description"

# Push and create PR
git push origin feature/HAP-96-feature-name
gh pr create --fill

# Merge PR
gh pr merge --squash
```

### Backend Commands
```bash
# Setup
mix deps.get
mix ecto.create && mix ecto.migrate

# Run
mix phx.server

# Test
mix test
mix credo
```

### Frontend Commands
```bash
# Setup
npm install

# Run
npx expo start

# Test
npm test
npm run lint
```

### Deployment Commands
```bash
# Backend (Docker)
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Frontend (EAS)
eas build --platform all
eas submit -p android
eas submit -p ios
```

---

*This document is a living document. Contributions and updates are welcome via PR to this repository.*
