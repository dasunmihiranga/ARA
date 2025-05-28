# Troubleshooting Guide

## Common Issues and Solutions

### Server Issues

#### Server Won't Start

**Symptoms:**
- Error message: "Failed to start server"
- Port already in use
- Permission denied

**Solutions:**
1. Check if port is in use:
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

2. Kill the process using the port:
```bash
# Windows
taskkill /PID <process_id> /F

# Linux/Mac
kill -9 <process_id>
```

3. Check permissions:
```bash
# Ensure script is executable
chmod +x scripts/start_server.sh
```

#### Server Crashes

**Symptoms:**
- Server stops unexpectedly
- Error logs show unhandled exceptions
- High memory usage

**Solutions:**
1. Check logs:
```bash
tail -f logs/server.log
```

2. Monitor system resources:
```bash
# Windows
taskmgr

# Linux
top
```

3. Adjust worker settings in `.env`:
```env
WORKERS=2
MAX_REQUESTS=1000
```

### Model Issues

#### Model Loading Fails

**Symptoms:**
- Error: "Failed to load model"
- Model not found
- Insufficient memory

**Solutions:**
1. Verify model installation:
```bash
ollama list
```

2. Check available models:
```bash
ollama pull <model_name>
```

3. Clear model cache:
```bash
ollama rm <model_name>
ollama pull <model_name>
```

#### Model Performance Issues

**Symptoms:**
- Slow response times
- High memory usage
- GPU not utilized

**Solutions:**
1. Check model settings:
```yaml
# config/models.yaml
model_settings:
  num_threads: 4
  batch_size: 32
```

2. Monitor GPU usage:
```bash
# Windows
nvidia-smi

# Linux
nvidia-smi -l 1
```

3. Adjust model parameters:
```python
model_params = {
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 0.9
}
```

### Search Issues

#### Search Returns No Results

**Symptoms:**
- Empty results list
- Timeout errors
- Rate limiting

**Solutions:**
1. Check search configuration:
```python
search_params = {
    "timeout": 30,
    "max_retries": 3,
    "sources": ["duckduckgo", "searx"]
}
```

2. Verify API keys:
```python
# Check environment variables
print(os.getenv("SEARX_API_KEY"))
```

3. Test individual sources:
```python
searcher = DuckDuckGoSearcher()
results = searcher.search("test query")
```

#### Search Timeout

**Symptoms:**
- Long response times
- Connection errors
- Partial results

**Solutions:**
1. Adjust timeout settings:
```python
search_params = {
    "timeout": 60,
    "connect_timeout": 10
}
```

2. Implement retry logic:
```python
@retry(max_attempts=3, delay=1)
def search_with_retry(query: str) -> List[SearchResult]:
    return searcher.search(query)
```

3. Use async search:
```python
async def async_search(query: str) -> List[SearchResult]:
    async with aiohttp.ClientSession() as session:
        tasks = [
            search_source(session, query)
            for source in sources
        ]
        results = await asyncio.gather(*tasks)
    return results
```

### Extraction Issues

#### Content Extraction Fails

**Symptoms:**
- Empty content
- Malformed HTML
- Encoding errors

**Solutions:**
1. Check extraction rules:
```yaml
# config/extraction_rules.yaml
web_content:
  selectors:
    main_content: "article, .content, #main"
  exclusions:
    - "nav"
    - "footer"
    - ".ads"
```

2. Verify URL accessibility:
```python
def check_url(url: str) -> bool:
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False
```

3. Handle different encodings:
```python
def extract_with_encoding(url: str) -> str:
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    return response.text
```

#### PDF Extraction Issues

**Symptoms:**
- Corrupted PDF
- Missing text
- Layout problems

**Solutions:**
1. Check PDF library:
```python
import PyPDF2

def verify_pdf(file_path: str) -> bool:
    try:
        with open(file_path, 'rb') as file:
            PyPDF2.PdfReader(file)
        return True
    except:
        return False
```

2. Use alternative extraction:
```python
def extract_pdf_text(file_path: str) -> str:
    try:
        # Try PyPDF2 first
        return extract_with_pypdf2(file_path)
    except:
        # Fallback to pdfplumber
        return extract_with_pdfplumber(file_path)
```

3. Handle scanned PDFs:
```python
def extract_scanned_pdf(file_path: str) -> str:
    # Convert to images
    images = convert_pdf_to_images(file_path)
    # OCR each image
    text = ""
    for image in images:
        text += perform_ocr(image)
    return text
```

### Analysis Issues

#### Analysis Fails

**Symptoms:**
- Empty analysis
- Invalid results
- Model errors

**Solutions:**
1. Check analysis templates:
```yaml
# config/analysis_templates.yaml
summarization:
  template: |
    Summarize the following text in {length} words:
    {text}
  parameters:
    length: 200
```

2. Verify input format:
```python
def validate_input(text: str) -> bool:
    return len(text.strip()) > 0 and len(text) < 10000
```

3. Handle model errors:
```python
def analyze_with_fallback(text: str) -> AnalysisResult:
    try:
        return primary_analyzer.analyze(text)
    except:
        return fallback_analyzer.analyze(text)
```

#### Performance Issues

**Symptoms:**
- Slow analysis
- High resource usage
- Timeout errors

**Solutions:**
1. Implement caching:
```python
@lru_cache(maxsize=1000)
def cached_analysis(text: str) -> AnalysisResult:
    return analyzer.analyze(text)
```

2. Use batch processing:
```python
def batch_analyze(texts: List[str]) -> List[AnalysisResult]:
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(analyzer.analyze, texts))
    return results
```

3. Optimize model parameters:
```python
model_params = {
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 0.9
}
```

### Storage Issues

#### Vector Store Problems

**Symptoms:**
- Failed queries
- Slow performance
- Memory issues

**Solutions:**
1. Check ChromaDB configuration:
```python
import chromadb

client = chromadb.Client(
    Settings(
        persist_directory="data/vector_store",
        anonymized_telemetry=False
    )
)
```

2. Optimize index:
```python
def optimize_index():
    collection = client.get_collection("documents")
    collection.reindex()
```

3. Monitor storage:
```python
def check_storage():
    total_size = get_directory_size("data/vector_store")
    if total_size > 10 * 1024 * 1024 * 1024:  # 10GB
        cleanup_old_vectors()
```

#### Cache Issues

**Symptoms:**
- Stale data
- Memory overflow
- Cache misses

**Solutions:**
1. Implement TTL:
```python
from datetime import datetime, timedelta

class Cache:
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds
        self.cache = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return value
        return None
```

2. Use LRU cache:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_function(param: str) -> Result:
    return expensive_operation(param)
```

3. Implement cache cleanup:
```python
def cleanup_cache():
    current_time = datetime.now()
    expired_keys = [
        key for key, (_, timestamp) in cache.items()
        if current_time - timestamp > timedelta(seconds=ttl)
    ]
    for key in expired_keys:
        del cache[key]
```

### API Issues

#### Authentication Problems

**Symptoms:**
- 401 Unauthorized
- Invalid token
- Expired credentials

**Solutions:**
1. Check API key:
```python
def validate_api_key(key: str) -> bool:
    return key in valid_keys and not is_expired(key)
```

2. Implement token refresh:
```python
def refresh_token(old_token: str) -> str:
    if is_expired(old_token):
        return generate_new_token()
    return old_token
```

3. Handle authentication errors:
```python
def handle_auth_error(response: Response) -> None:
    if response.status_code == 401:
        token = refresh_token(current_token)
        retry_request(token)
```

#### Rate Limiting

**Symptoms:**
- 429 Too Many Requests
- Slow responses
- Blocked requests

**Solutions:**
1. Implement rate limiting:
```python
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=100, period=60)
def rate_limited_function():
    pass
```

2. Use exponential backoff:
```python
def exponential_backoff(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(3):
            try:
                return func(*args, **kwargs)
            except RateLimitError:
                time.sleep(2 ** attempt)
        raise MaxRetriesExceeded()
    return wrapper
```

3. Monitor usage:
```python
def track_api_usage():
    current_usage = get_current_usage()
    if current_usage > threshold:
        notify_admin()
```

## Debugging Tools

### Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='debug.log'
)

logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

### Profiling

```python
import cProfile
import pstats

def profile_function(func):
    profiler = cProfile.Profile()
    profiler.enable()
    result = func()
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats()
    return result
```

### Memory Profiling

```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    # Implementation
    pass
```

## Getting Help

### Support Channels

1. **GitHub Issues**
   - Create a new issue
   - Include error logs
   - Provide reproduction steps

2. **Community Forums**
   - Post in relevant category
   - Share code snippets
   - Describe environment

3. **Documentation**
   - Check API reference
   - Review user guide
   - Search existing issues

### Reporting Bugs

1. **Required Information**
   - Error message
   - Stack trace
   - Environment details
   - Steps to reproduce

2. **Bug Template**
```markdown
## Description
[Detailed description of the issue]

## Steps to Reproduce
1. [First step]
2. [Second step]
3. [And so on...]

## Expected Behavior
[What you expected to happen]

## Actual Behavior
[What actually happened]

## Environment
- OS: [e.g., Windows 10]
- Python Version: [e.g., 3.8.5]
- Package Version: [e.g., 1.0.0]

## Additional Context
[Any additional information]
```

3. **Screenshots/Logs**
   - Error messages
   - Console output
   - Relevant logs

## Maintenance

### Regular Checks

1. **System Health**
```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check CPU usage
top
```

2. **Log Rotation**
```bash
# Configure logrotate
/etc/logrotate.d/research-assistant
```

3. **Backup**
```bash
# Backup data
tar -czf backup.tar.gz data/

# Backup configuration
cp -r config/ config_backup/
```

### Updates

1. **Check for Updates**
```bash
git fetch origin
git status
```

2. **Update Dependencies**
```bash
pip install -r requirements.txt --upgrade
```

3. **Update Models**
```bash
./scripts/download_models.sh
```

### Cleanup

1. **Clear Cache**
```bash
rm -rf data/cache/*
```

2. **Remove Old Logs**
```bash
find logs/ -type f -mtime +30 -delete
```

3. **Clean Temporary Files**
```bash
rm -rf data/temp/*
``` 