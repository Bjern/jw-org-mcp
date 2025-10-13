# Product Requirements Document: JW.Org MCP Tool

## 1. Executive Summary

The JW.Org MCP Tool is a Model Context Protocol (MCP) server designed to provide controlled, verifiable, and reliable access to content from jw.org for AI applications and LLM integrations. This tool addresses the critical challenge of ensuring doctrinal accuracy in AI responses by serving content exclusively from official jw.org sources, eliminating the risk of hallucinations or external contamination when handling scriptural and doctrinal queries.

### 1.1 Key Business Objectives

- **Ensure Source Integrity**: Guarantee that all scriptural and doctrinal information comes exclusively from jw.org
- **Enable AI Integration**: Provide a standardized MCP interface for AI applications to access jw.org content
- **Optimize Performance**: Deliver fast, bandwidth-efficient responses through compression and intelligent caching
- **Maintain Transparency**: Include verifiable source references in all responses

### 1.2 Success Metrics

- 100% source verification from jw.org domains
- < 2 second average response time for search queries
- 80% minimum test coverage
- Zero PII logging incidents
- 99.9% uptime availability

## 2. Product Overview

### 2.1 Problem Statement

Large Language Models (LLMs) cannot inherently guarantee that scriptural or doctrinal information originates from authoritative sources. When asked about biblical topics or religious doctrine, AI systems may:
- Generate inaccurate information from training data
- Mix information from multiple religious sources
- Produce hallucinations that appear credible but are incorrect
- Lack verifiable references for their responses

### 2.2 Solution

The JW.Org MCP Tool acts as a trusted intermediary between AI applications and jw.org content, providing:
- Direct API access to jw.org's search infrastructure
- Structured, machine-readable responses
- Content verification through source URLs
- Intelligent query parsing to extract meaningful search terms
- Support for multiple content types (articles, videos, publications, scriptures)

### 2.3 Target Users

- **Primary**: AI application developers integrating religious content
- **Secondary**: Desktop tool developers using MCP ecosystem
- **Tertiary**: Research applications requiring verified scriptural references

## 3. Functional Requirements

### 3.1 Core Features

#### 3.1.1 Search Functionality

**Description**: Enable comprehensive searching across jw.org content

**Requirements**:
- Support multiple search filters:
  - `all` - Search across all content types
  - `publications` - Search within publications only
  - `videos` - Search video content
  - `audio` - Search audio content (music, dramas)
  - `bible` - Search scripture verses
  - `indexes` - Search publication indexes
- Support language selection (initially English with code `E`)
- Support pagination for large result sets
- Support sorting options (relevance, newest, oldest)

**Acceptance Criteria**:
- Search results return within 2 seconds
- Results match jw.org website search functionality
- Proper handling of special characters and phrases

#### 3.1.2 Authentication Management

**Description**: Handle JWT-based authentication with jw.org APIs

**Requirements**:
- Automatic CDN discovery from jw.org homepage
- JWT token acquisition from CDN endpoint
- Token refresh before expiration
- Secure token storage during session

**Acceptance Criteria**:
- Successfully authenticate on first request
- Automatically refresh tokens before expiry
- Handle authentication failures gracefully

#### 3.1.3 Content Retrieval

**Description**: Fetch and parse article content from wol.jw.org

**Requirements**:
- Extract article content from HTML structure
- Parse paragraph elements with proper ordering
- Remove formatting artifacts (highlighting spans)
- Preserve scripture references and citations

**Acceptance Criteria**:
- Content matches source article exactly
- Proper paragraph ordering maintained
- No HTML artifacts in output

#### 3.1.4 Query Intelligence

**Description**: Parse user queries to extract meaningful search terms

**Requirements**:
- Separate search subjects from question framing
- Handle natural language queries
- Provide parameter hints for LLM integration

**Example**:
- Input: "What does the Bible say about peace and security?"
- Extracted: "peace and security"

**Acceptance Criteria**:
- Correctly extract search terms in 90% of cases
- Document parameter usage for LLM developers

### 3.2 MCP Interface

#### 3.2.1 Tool Endpoints

**search_content**
```python
Parameters:
  - query: str (required) - The search term/phrase
  - filter: str (optional) - Content type filter
  - language: str (optional, default="E") - Language code
  - limit: int (optional, default=10) - Result limit
  - offset: int (optional, default=0) - Pagination offset

Returns:
  - results: List of search results
  - source_url: Verification URL
  - timestamp: ISO 8601 timestamp
  - total_results: Total count
```

**get_article**
```python
Parameters:
  - url: str (required) - Article URL from search results

Returns:
  - title: Article title
  - content: Full article text
  - references: Scripture references
  - source_url: Original URL
  - timestamp: ISO 8601 timestamp
```

**get_scripture**
```python
Parameters:
  - reference: str (required) - Scripture reference
  - translation: str (optional, default="nwtsty") - Bible translation

Returns:
  - text: Scripture text
  - reference: Formatted reference
  - context: Surrounding verses
  - source_url: Verification URL
  - timestamp: ISO 8601 timestamp
```

### 3.3 Response Format

All responses must include:
```json
{
  "data": {
    // Response specific data
  },
  "metadata": {
    "source_domain": "jw.org",
    "source_url": "https://...",
    "timestamp": "2024-01-01T00:00:00Z",
    "query_params": {},
    "cache_hit": false
  }
}
```

## 4. Non-Functional Requirements

### 4.1 Performance

- **Response Time**: < 2 seconds for search queries
- **Throughput**: Support 100 concurrent requests
- **Caching**: Implement 15-minute cache for repeated queries
- **Compression**: Use Brotli compression for all requests

### 4.2 Security

- **Authentication**: Secure JWT token handling
- **Privacy**: No logging of personally identifiable information
- **Input Validation**: Sanitize all user inputs
- **HTTPS Only**: All external requests use HTTPS

### 4.3 Reliability

- **Availability**: 99.9% uptime
- **Error Handling**: Graceful degradation on API failures
- **Retry Logic**: Implement exponential backoff for failed requests
- **Health Check**: Provide `/health` endpoint for monitoring

### 4.4 Scalability

- **Async I/O**: Use async patterns for network operations
- **Connection Pooling**: Reuse HTTP connections
- **Resource Limits**: Implement request rate limiting
- **Horizontal Scaling**: Stateless design for multiple instances

### 4.5 Maintainability

- **Code Quality**: PEP8 compliance, type hints
- **Testing**: Minimum 80% code coverage
- **Documentation**: Comprehensive API documentation
- **Logging**: Structured logging for debugging

## 5. Technical Architecture

### 5.1 System Components

```
┌─────────────────┐
│   MCP Client    │
│  (AI/Desktop)   │
└────────┬────────┘
         │
    MCP Protocol
         │
┌────────▼────────┐
│   MCP Server    │
│  (FastMCP)      │
├─────────────────┤
│ • Request Router│
│ • Query Parser  │
│ • Cache Manager │
└────────┬────────┘
         │
┌────────▼────────┐
│  JW.Org Client  │
├─────────────────┤
│ • Auth Manager  │
│ • API Client    │
│ • HTML Parser   │
└────────┬────────┘
         │
    HTTP/HTTPS
         │
┌────────▼────────┐
│   JW.Org APIs   │
├─────────────────┤
│ • CDN Discovery │
│ • JWT Auth      │
│ • Search API    │
│ • Content API   │
└─────────────────┘
```

### 5.2 Data Flow

1. **Authentication Flow**:
   - Discover CDN URL from jw.org homepage
   - Request JWT token from CDN
   - Store token for session duration
   - Refresh before expiration

2. **Search Flow**:
   - Receive search query from MCP client
   - Parse query to extract search terms
   - Check cache for existing results
   - Make authenticated API request if cache miss
   - Parse and structure response
   - Cache results
   - Return structured data to client

3. **Content Retrieval Flow**:
   - Receive article URL from client
   - Fetch HTML content from wol.jw.org
   - Parse article structure
   - Extract paragraphs and references
   - Return structured content

### 5.3 Technology Stack

| Component | Technology | Justification |
|-----------|------------|---------------|
| Runtime | Python 3.13+ | Modern async support, type hints |
| MCP Framework | FastMCP | Official MCP implementation |
| HTTP Client | Requests/HTTPX | Reliable, supports compression |
| HTML Parser | BeautifulSoup4 | Robust HTML parsing |
| Compression | Brotli | Optimal compression for text |
| Testing | Pytest | Industry standard, async support |
| Linting | Ruff | Fast, comprehensive checks |
| Package Management | UV | Modern, fast dependency resolution |

## 6. Implementation Phases

### Phase 1: Core Infrastructure (Week 1-2)
- [ ] Project setup and configuration
- [ ] Basic MCP server implementation
- [ ] Authentication flow with jw.org
- [ ] CDN discovery mechanism

### Phase 2: Search Functionality (Week 3-4)
- [ ] Search endpoint implementation
- [ ] Query parsing logic
- [ ] Response structuring
- [ ] Basic caching layer

### Phase 3: Content Retrieval (Week 5-6)
- [ ] Article fetching and parsing
- [ ] Scripture reference handling
- [ ] Content extraction optimization
- [ ] Error handling improvements

### Phase 4: Quality & Performance (Week 7-8)
- [ ] Comprehensive testing suite
- [ ] Performance optimization
- [ ] Documentation completion
- [ ] Security audit

### Phase 5: Production Readiness (Week 9-10)
- [ ] Deployment configuration
- [ ] Monitoring setup
- [ ] Rate limiting implementation
- [ ] Final testing and validation

## 7. Testing Strategy

### 7.1 Unit Testing
- Test individual components in isolation
- Mock external API calls
- Achieve 80% code coverage

### 7.2 Integration Testing
- Test authentication flow
- Test search functionality
- Test content retrieval
- Verify response formats

### 7.3 Performance Testing
- Load testing with concurrent requests
- Response time validation
- Cache effectiveness measurement

### 7.4 Security Testing
- Input validation testing
- Authentication security
- PII leak prevention

## 8. Documentation Requirements

### 8.1 Developer Documentation
- API reference with examples
- Integration guide for MCP clients
- Troubleshooting guide

### 8.2 Code Documentation
- Inline comments for complex logic
- Docstrings for all public functions
- Type hints throughout

### 8.3 Operational Documentation
- Deployment instructions
- Configuration guide
- Monitoring setup

## 9. Risk Assessment

### 9.1 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| API Changes | High | Medium | Version detection, graceful degradation |
| Rate Limiting | Medium | High | Caching, request throttling |
| Token Expiry | Low | High | Proactive refresh, retry logic |
| Network Failures | Medium | Medium | Retry with backoff, circuit breaker |

### 9.2 Business Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Content Accuracy | High | Low | Direct API usage, verification |
| Performance Issues | Medium | Medium | Caching, optimization |
| Adoption Barriers | Medium | Medium | Clear documentation, examples |

## 10. Success Criteria

### 10.1 Launch Criteria
- [ ] All core features implemented
- [ ] 80% test coverage achieved
- [ ] Documentation complete
- [ ] Security audit passed
- [ ] Performance benchmarks met

### 10.2 Post-Launch Metrics
- API response time < 2 seconds (p95)
- Zero security incidents
- 99.9% uptime maintained
- Positive developer feedback

## 11. Future Enhancements

### 11.1 Short Term (3-6 months)
- Additional language support
- Advanced caching strategies
- Batch request support
- WebSocket support for real-time updates

### 11.2 Long Term (6-12 months)
- Multi-region deployment
- Advanced query understanding with NLP
- Offline content packages
- Integration with more jw.org services

## 12. Appendices

### Appendix A: API Response Examples

#### Search Response
```json
{
  "data": {
    "results": [
      {
        "title": "Peace and Security—The Hope",
        "snippet": "The General Assembly of the United Nations...",
        "url": "https://wol.jw.org/...",
        "type": "article",
        "publication": "The Watchtower",
        "year": 1985
      }
    ],
    "total": 10000,
    "page": 1
  },
  "metadata": {
    "source_domain": "jw.org",
    "source_url": "https://b.jw-cdn.org/apis/search/...",
    "timestamp": "2024-01-01T00:00:00Z",
    "query_params": {
      "query": "peace and security",
      "filter": "all",
      "language": "E"
    },
    "cache_hit": false
  }
}
```

### Appendix B: Error Response Format
```json
{
  "error": {
    "code": "AUTH_FAILED",
    "message": "Failed to authenticate with jw.org",
    "details": "Token refresh failed after 3 attempts",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### Appendix C: Language Codes
| Code | Language |
|------|----------|
| E | English |
| S | Spanish |
| F | French |
| P | Portuguese |
| I | Italian |
| G | German |
| J | Japanese |
| K | Korean |
| CH | Chinese |

---

**Document Version**: 1.0.0
**Last Updated**: 2024-10-14
**Author**: Product Engineering Team
**Status**: Draft