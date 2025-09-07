# PyDoll MCP Browser Tools

A comprehensive browser automation toolkit providing Chrome/Chromium control through MCP (Model Context Protocol).

## Quick Start

```python
# Create and start browser session
mcp__pydoll-browser__create_browser_session(session_id="my-session", headless=True)
mcp__pydoll-browser__start_browser_session(session_id="my-session")

# Create tab and navigate
mcp__pydoll-browser__create_tab(browser_session_id="my-session", tab_id="tab1", url="https://example.com")
mcp__pydoll-browser__navigate(tab_id="tab1", url="https://google.com")

# Find and interact with elements
mcp__pydoll-browser__find_elements(tab_id="tab1", base_element_id="root", selector_type="css", selector_value="input")
mcp__pydoll-browser__get_element_text(element_id="element_id")

# Cleanup
mcp__pydoll-browser__close_browser_session(session_id="my-session")
```

## Available Tools

### Session Management
- `create_browser_session` - Initialize browser with configuration options
- `start_browser_session` - Start browser and create initial tab
- `close_browser_session` - Close browser and cleanup resources
- `list_sessions` - View active browser and tab sessions
- `get_session_info` - Get detailed session information

### Tab Operations
- `create_tab` - Create new tab with optional URL
- `close_tab` - Close specific tab
- `bring_tab_to_front` - Focus tab
- `navigate` - Navigate to URL with wait conditions
- `go_back` / `go_forward` - Browser history navigation
- `refresh_page` - Reload current page

### Element Finding & Interaction
- `find_elements` - Locate elements using CSS, XPath, ID, name, tag, class selectors
- `wait_for_element` - Wait for element to appear
- `click_element` / `click_element_js` - Click elements
- `type_text` - Input text into elements
- `clear_text` - Clear input fields
- `hover_element` - Mouse hover actions
- `scroll_element` - Scroll operations
- `drag_and_drop` - Drag and drop actions

### Element Properties
- `get_element_text` - Extract visible text
- `get_element_attribute` - Get HTML attributes
- `get_element_property` - Get JavaScript properties
- `get_element_html` - Get element HTML content
- `get_element_bounds` - Get position and dimensions
- `is_element_visible` / `is_element_enabled` / `is_element_selected` - State checks

### Page Information
- `get_page_title` - Current page title
- `get_page_url` - Current URL
- `get_page_source` - Complete page HTML
- `wait_for_page_load` - Wait for page completion

### JavaScript Execution
- `execute_script` - Run JavaScript in page context
- `execute_script_on_element` - Run JavaScript with element context
- `wait_for_function` - Wait for JavaScript condition

### File Operations
- `take_screenshot` - Capture page or element screenshots
- `save_pdf` - Generate PDF from page
- `upload_file` - Handle file uploads
- `download_file` - Download files from URLs

### Event Monitoring
- `enable_page_events` - Monitor page load events
- `enable_network_events` - Track network requests
- `enable_runtime_events` - Capture console and errors
- `get_network_logs` - Retrieve request logs

### Advanced Features
- `handle_alert` - Manage JavaScript dialogs
- `set_cookies` / `get_cookies` / `delete_cookies` - Cookie management

### Utilities
- `cleanup_elements` - Clear cached element references
- `key_down` / `key_up` / `press_key` - Keyboard actions

## Configuration Options

### Browser Session Parameters
- `headless` - Run without GUI (default: true)
- `window_size` - Browser dimensions (e.g., "1920,1080")
- `user_agent` - Custom user agent string
- `disable_images` - Block image loading
- `disable_javascript` - Disable JS execution
- `proxy` - Proxy server configuration

### Selector Types
- `css` - CSS selectors
- `xpath` - XPath expressions
- `id` - Element ID
- `name` - Element name attribute
- `tag` - HTML tag name
- `class` - CSS class name

## Error Handling

Tools return error messages for common issues:
- Invalid session/tab IDs
- Element not found
- Navigation timeouts
- Script execution failures

## Requirements

- Chrome/Chromium browser installed
- PyDoll MCP server running
- Appropriate system permissions for browser automation
