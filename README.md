# Hyperview DevOps / LLMOps Toolchain

Shared DevOps repository for the Hyperview ecosystem.

## Repositories

- **workout_backend**: Elixir/Phoenix backend service
- **workout_frontend**: React Native/Expo mobile application  
- **devops**: This repository - shared documentation and tooling

## Documentation

- [Preproduction configuration and beta key rotation](docs/PREPROD_CONFIGURATION.md)
- [SDLC Workflow](docs/sdlc.md) - Software Development Lifecycle (HAP-96)

## Quick Links

- [Linear Project: DevOps/LLMOps toolchain](https://linear.app/hapteo/project/4b600597-75ac-4b26-b5bd-716640d9ac69)
- Issue: [HAP-96](https://linear.app/hapteo/issue/HAP-96)

## Structure

```
devops/
├── config/          # Shared configuration files
├── scripts/         # Deployment and automation scripts
├── docs/            # Documentation
│   └── sdlc.md      # SDLC workflow (HAP-96)
└── README.md        # This file
```

## Getting Started

### Clone this repository

```bash
git clone /Users/regismartin/dev/hyperview/hyperview/devops
git clone /Users/regismartin/dev/hyperview/hyperview/workout_backend
Git clone /Users/regismartin/dev/hyperview/hyperview/workout_frontend
```

### Follow the SDLC

All development should follow the workflow documented in [docs/sdlc.md](docs/sdlc.md).

---

**Maintainer**: Régis Martin (@regismartin)  
**Project**: Hapteo  
**License**: Private
