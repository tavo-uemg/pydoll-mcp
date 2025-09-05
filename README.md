# PyDoll MCP Server

A comprehensive browser automation MCP (Model Context Protocol) server built on the PyDoll library, providing programmatic control over Chrome browser instances through the DevTools Protocol.

## Overview

The PyDoll MCP Server enables advanced web automation, testing, and scraping capabilities through a rich set of tools for browser control, element interaction, JavaScript execution, and more. It supports headless and non-headless modes, handles modern web challenges like Cloudflare protection, and provides extensive monitoring and debugging capabilities.

## Features

### Core Browser Management
- **Session Management**: Create, start, and manage multiple browser sessions
- **Tab Control**: Create, navigate, close, and switch between tabs
- **Configuration**: Customizable Chrome options including headless mode, user agents, proxies

### Element Interaction
- **Element Finding**: Locate elements using CSS selectors, XPath, ID, name, tag, or class
- **User Actions**: Click, type, hover, drag-and-drop, scroll
- **Element State**: Check visibility, enabled status, selection state, and interactability
- **Element Relationships**: Navigate parent, child, and sibling elements

### Page Interaction
- **Navigation**: Go to URLs, back/forward navigation, page refresh
- **JavaScript Execution**: Execute scripts in page context or on specific elements
- **Waiting**: Wait for page load, elements to appear, or custom conditions
- **Content Access**: Get page title, URL, HTML source

### Media and Files
- **Screenshots**: Capture full page or element-specific screenshots in PNG/JPEG
- **PDF Generation**: Save pages as PDF documents
- **File Operations**: Upload files, download files, handle file chooser dialogs

### Advanced Features
- **Cloudflare Bypass**: Automatic detection and bypass of Cloudflare protection
- **Network Monitoring**: Track HTTP requests/responses, intercept and modify requests
- **Event Handling**: Monitor page events, DOM changes, console messages
- **Cookie Management**: Get, set, and delete cookies
- **Alert Handling**: Manage JavaScript alerts, confirms, and prompts

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# The PyDoll MCP server is provided as a compiled binary
# Ensure the pydoll-mcp executable has proper permissions
chmod +x pydoll-mcp
```

## Requirements

- Python 3.7+
- Chrome/Chromium browser
- Required Python packages:
  - pydoll-python>=2.8.0
  - aiohttp>=3.9.5
  - websockets>=14.0
  - aiofiles>=23.2.1
  - typing_extensions>=4.14.0

## Quick Start

### Basic Browser Automation

```python
# Create and start a browser session
session_id = "my_session"
create_browser_session(session_id=session_id, headless=True)
start_browser_session(session_id=session_id)

# Create a tab and navigate
tab_id = "my_tab"
create_tab(browser_session_id=session_id, tab_id=tab_id, url="https://example.com")

# Take a screenshot
screenshot = take_screenshot(tab_id=tab_id, format="png")

# Find and interact with elements
elements = find_elements(tab_id=tab_id, base_element_id="root", 
                        selector_type="css", selector_value="button")

# Clean up
close_browser_session(session_id=session_id)
```

### Web Scraping Example

```python
# Navigate to target site
navigate(tab_id=tab_id, url="https://httpbin.org")

# Find data elements
data_elements = find_elements(tab_id=tab_id, base_element_id="root",
                             selector_type="css", selector_value=".data")

# Extract text content
for element_id in data_elements:
    text = get_element_text(element_id=element_id)
    print(f"Found data: {text}")
```

## Available Tools

### Browser Session Management
- `create_browser_session` - Create a new browser session
- `start_browser_session` - Start an existing browser session
- `close_browser_session` - Close and cleanup browser session
- `list_sessions` - List all active sessions
- `get_session_info` - Get detailed session information

### Tab Management
- `create_tab` - Create new tab with optional initial URL
- `close_tab` - Close a browser tab
- `bring_tab_to_front` - Focus a specific tab
- `navigate` - Navigate to URL with load waiting
- `go_back` / `go_forward` - Browser history navigation
- `refresh_page` - Reload current page

### Element Finding & Interaction
- `find_elements` - Find multiple elements using selectors
- `click_element` - Click element with mouse simulation
- `click_element_js` - Click using JavaScript
- `type_text` - Type text into input elements
- `clear_text` - Clear input element text
- `hover_element` - Mouse hover over element
- `scroll_element` - Scroll element into view
- `drag_and_drop` - Drag element to target location

### Element State & Properties
- `get_element_text` - Get visible text content
- `get_element_attribute` - Get HTML attribute value
- `get_element_property` - Get JavaScript property
- `get_element_html` - Get element HTML content
- `get_element_bounds` - Get position and dimensions
- `is_element_visible` - Check visibility
- `is_element_enabled` - Check if enabled
- `is_element_selected` - Check selection state
- `is_element_interactable` - Check full interactability

### Page Information & Control
- `get_page_title` - Get current page title
- `get_page_url` - Get current page URL
- `get_page_source` - Get full HTML source
- `execute_script` - Execute JavaScript in page
- `execute_script_on_element` - Execute JS with element context

### Waiting & Synchronization
- `wait_for_page_load` - Wait for page to finish loading
- `wait_for_element` - Wait for element to appear
- `wait_for_function` - Wait for JS function to return true
- `element_wait_until` - Wait for element condition

### Media & Files
- `take_screenshot` - Capture screenshots (PNG/JPEG)
- `save_pdf` - Generate PDF documents
- `upload_file` - Upload files through input elements
- `download_file` - Download files from URLs
- `expect_file_chooser` - Handle file picker dialogs

### Network & Monitoring
- `enable_network_events` - Enable request/response monitoring
- `get_network_logs` - Retrieve network activity logs
- `continue_request` - Modify intercepted requests
- `fail_request` - Block specific requests
- `fulfill_request` - Provide custom responses

### Cloudflare & Security
- `bypass_cloudflare` - Automatically bypass CF protection
- `enable_auto_solve_cloudflare` - Background CF solving
- `disable_auto_solve_cloudflare` - Disable auto-solving

### Cookies & Storage
- `get_cookies` - Retrieve cookies for domain
- `set_cookies` - Set cookies for domain  
- `delete_cookies` - Remove specific cookies

### Dialog & Alert Handling
- `handle_alert` - Respond to JavaScript dialogs
- `has_dialog` - Check for active dialogs
- `get_dialog_message` - Get dialog text content

### Event Monitoring
- `enable_page_events` - Monitor page lifecycle events
- `enable_runtime_events` - Track console/exception events
- `enable_dom_events` - Monitor DOM changes
- `get_event_logs` - Retrieve captured events
- `register_event_callback` - Set up event handlers

### Utility & Cleanup
- `cleanup_elements` - Clear cached element references
- `set_browser_preferences` - Configure browser settings

## Advanced Configuration

### Browser Options
```python
create_browser_session(
    session_id="advanced_session",
    headless=False,                    # Run with GUI
    window_size="1920,1080",          # Set window size
    user_agent="Custom Agent 1.0",    # Custom user agent
    proxy="http://proxy:8080",        # Proxy server
    disable_images=True,              # Block images for speed
    disable_javascript=False,         # Enable JavaScript
    additional_args=["--no-sandbox"]  # Extra Chrome flags
)
```

### Network Interception
```python
# Enable network monitoring
enable_network_events(tab_id=tab_id)

# Get request logs
logs = get_network_logs(tab_id=tab_id, filter_pattern="*.json", limit=50)

# Modify requests (requires interceptor setup)
continue_request(request_id="req_123", 
                headers={"Authorization": "Bearer token"})
```

### Event Monitoring
```python
# Enable comprehensive monitoring
enable_page_events(tab_id=tab_id)
enable_runtime_events(tab_id=tab_id)
enable_dom_events(tab_id=tab_id)

# Retrieve event logs
events = get_event_logs(tab_id=tab_id)
```

## Error Handling

The PyDoll MCP Server provides detailed error messages for common scenarios:

- **Element not found**: Returns empty results or specific error messages
- **Timeout errors**: Configurable timeout periods for operations
- **Network failures**: Comprehensive request/response error reporting
- **JavaScript errors**: Runtime exception capture and reporting
- **Session management**: Clear status reporting for session operations

## Performance Considerations

- **Headless Mode**: Use headless=True for better performance in production
- **Image Loading**: Disable images with disable_images=True for faster page loads
- **Element Caching**: Elements are automatically cached and cleaned up
- **Session Reuse**: Reuse browser sessions when possible to avoid startup overhead
- **Resource Cleanup**: Always close sessions when finished

## Browser Compatibility

- **Chrome/Chromium**: Primary support (recommended)
- **Chrome DevTools Protocol**: Uses CDP for reliable automation
- **Cross-platform**: Works on Windows, macOS, and Linux

## Security Features

- **Cloudflare Bypass**: Handles modern bot detection systems
- **Request Interception**: Full control over network traffic
- **Cookie Management**: Secure cookie handling and persistence
- **Proxy Support**: Route traffic through proxy servers
- **User Agent Spoofing**: Customize browser identification

## Use Cases

- **Web Scraping**: Extract data from dynamic websites
- **Automated Testing**: E2E testing of web applications
- **Performance Monitoring**: Track page load times and network activity
- **Content Generation**: Capture screenshots and generate PDFs
- **Bot Detection Bypass**: Navigate protected sites automatically
- **Data Collection**: Gather structured data from multiple sources

## Troubleshooting

### Common Issues

1. **Chrome not found**: Ensure Chrome/Chromium is installed and accessible
2. **Permission errors**: Check that the pydoll-mcp binary has execute permissions
3. **Network timeouts**: Increase timeout values for slow pages
4. **Element not found**: Use wait conditions before element interaction
5. **Memory usage**: Close unused sessions and tabs regularly

### Debug Mode

Enable verbose logging by examining network events and runtime errors:

```python
enable_runtime_events(tab_id=tab_id)
logs = get_event_logs(tab_id=tab_id)
```

## Contributing

This is a closed-source MCP server implementation. For issues or feature requests, please contact the development team.

## License

Proprietary software. All rights reserved.

---

*PyDoll MCP Server - Advanced Browser Automation for the Modern Web*