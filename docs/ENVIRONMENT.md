# Environment Setup

## Local Development

### macOS

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.11
brew install postgresql
brew install redis

# Start services
brew services start postgresql
brew services start redis
```

### Ubuntu/Debian

```bash
# Update packages
sudo apt update

# Install dependencies
sudo apt install python3.11 python3.11-dev
sudo apt install postgresql postgresql-contrib
sudo apt install redis-server

# Start services
sudo service postgresql start
sudo service redis-server start
```

### Windows

Use WSL2 (Windows Subsystem for Linux):

```bash
# Follow Ubuntu instructions above
# Or use Docker Desktop
```

## Docker (Recommended)

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Run Wojak Capital
docker-compose up -d
```
