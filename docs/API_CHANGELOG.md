# API Changelog

## v1.0.0 (2026-04-16)

### New Endpoints
- `GET /api/v1/agents/status` - Agent status
- `POST /api/v1/trade/manual` - Manual trading
- `POST /api/v1/emergency-stop` - Emergency stop

### Changed
- Signal format now includes metadata
- WebSocket authentication required

### Deprecated
- Old signal endpoint (removed)

## v0.9.0 (2026-04-10)

### Added
- WebSocket support
- Real-time updates

### Changed
- Database schema

## v0.8.0 (2026-04-01)

### Added
- Initial REST API
- Health check endpoint
