# CRC Documentation MCP Server

An MCP (Model Context Protocol) server that provides intelligent access to CRC/OpenShift Local documentation. This server fetches, caches, and searches through official CRC documentation to answer questions about CRC or OpenShift Local.

## Features

- **Multi-source Documentation Access**: Fetches content from multiple CRC documentation sources
- **Intelligent Search**: Finds relevant sections based on query relevance scoring
- **Caching System**: Reduces API calls by caching fetched documentation
- **Clean Text Extraction**: Extracts readable content from HTML pages
- **MCP Integration**: Works seamlessly with MCP-compatible clients

## Documentation Sources

The server accesses the following CRC documentation sources:

- **CRC Docs**: https://crc.dev/docs - Official documentation
- **CRC Blog**: https://crc.dev/blog - Blog posts and announcements  
- **CRC Engineering**: https://crc.dev/engineering-docs - Engineering documentation

## Installation

### Prerequisites

- Python 3.13 or higher
- uv (recommended) or pip

### Install with uv (recommended)

```bash
# Clone the repository
git clone <repository-url>
cd crc-documentation

# Install dependencies
uv sync
```


## Usage

### Running the Server

Start the MCP server:

```bash
# With uv
uv run server.py

# With Python directly
python server.py
```

The server runs on stdio transport and is designed to be used with MCP-compatible clients.

### Using with Cursor/VSCode

#### Cursor Configuration

To use this MCP server with Cursor, add the following configuration to your Cursor settings:

1. Open Cursor Settings (Cmd/Ctrl + ,)
2. Search for "MCP" or go to Extensions → MCP
3. Add a new MCP server configuration:

```json
{
  "mcpServers": {
    "crcdocs": {
      "command": "/path/to/your/uv/binary",
      "args": [
        "--directory",
        "/path/to/your/crc-documentation",
        "run",
        "server.py"
      ]
    }
  }
}

```

#### Testing the Integration

Once configured, you can test the integration by:

1. Restart Cursor/VSCode
2. Open the MCP panel or use the command palette
3. Try asking questions like:
   - "How do I install CRC on Linux?"
   - "What are the system requirements for CRC?"
   - "How do I troubleshoot CRC startup issues?"

The server will search through CRC documentation and provide relevant answers.

### Available Tools

#### `crc_doc_query`

Query CRC documentation to get answers about CodeReady Containers or OpenShift Local.

**Parameters:**
- `query` (required): Your question about CRC or OpenShift Local
- `sources` (optional): List of specific sources to search (defaults to all sources)

**Example:**
```python
# Query all sources
result = await crc_doc_query("How do I install CRC on Linux?")

# Query specific sources
result = await crc_doc_query(
    "What are the system requirements?", 
    sources=["crc", "crc-blog"]
)
```

#### `clear_cache`

Clear the documentation cache to fetch fresh content on the next query.

**Example:**
```python
result = await clear_cache()
```

## Configuration

The server is configured through the following constants in `server.py`:

```python
DOC_SOURCES = {
    "crc": "https://crc.dev/docs",
    "crc-blog": "https://crc.dev/blog", 
    "crc-dev": "https://crc.dev/engineering-docs"
}
```

## How It Works

1. **Content Fetching**: The server fetches HTML content from CRC documentation sources
2. **Text Extraction**: Uses BeautifulSoup to extract clean, readable text from HTML
3. **Relevance Scoring**: Analyzes content to find sections most relevant to your query
4. **Caching**: Stores fetched content to improve performance on subsequent queries
5. **Response Formatting**: Returns structured results with source attribution


### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Logging

The server uses Python's built-in logging module. Logs are set to INFO level by default and include:

- Documentation fetching operations
- Error handling for failed requests
- Cache operations

## Support

For issues with this MCP server, please open an issue in the repository.
