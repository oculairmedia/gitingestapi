# GitIngest API

GitIngest API is a service that provides repository analysis and content ingestion capabilities through a simple HTTP interface.

## API Endpoints

### Repository Ingestion

```
GET /api/v1/ingest
```

Analyzes and ingests content from a GitHub repository.

#### Query Parameters

- `url` (required): The GitHub repository URL to analyze
- `max_file_size` (optional): Maximum file size to process in KB (default: 243)
- `pattern_type` (optional): Type of pattern matching to use (values: "exclude" or "include", default: "exclude")

#### Example Request

```bash
curl -X 'GET' \
  'http://localhost:8082/api/v1/ingest?url=https://github.com/username/repo&max_file_size=243&pattern_type=exclude' \
  -H 'accept: application/json'
```

#### Response Format

The API returns a JSON response containing:

- Repository summary
- Directory structure
- Analyzed file contents

Example response:
```json
{
  "summary": "Repository analysis summary...",
  "tree": "Directory structure...",
  "content": "Analyzed file contents..."
}
```

## Docker Deployment

The API can be deployed using Docker:

```bash
docker-compose up -d
```

This will start the API service on port 8082 (configurable in docker-compose.yml).

## Environment Variables

- `GITINGEST_URL`: Base URL for the API service (default: http://localhost:8082)
