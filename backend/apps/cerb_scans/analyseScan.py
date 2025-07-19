import asyncio
import base64
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse


class CaptureError(Exception):
    """Base exception for capture errors."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def to_dict(self) -> Dict:
        return {
            "error": self.message,
            "type": "capture_error"
        }

class ProxyError(CaptureError):
    """Exception raised when proxy connection fails."""
    def __init__(self, proxy: str, error: str):
        super().__init__(f"Proxy error with {proxy}: {error}")
        self.proxy = proxy
        self.error = error

    def to_dict(self) -> Dict:
        return {
            "proxy": self.proxy,
            "error": self.error,
            "type": "proxy_error"
        }

class SSLError(CaptureError):
    """Exception raised when SSL verification fails."""
    def __init__(self, url: str, error: str):
        super().__init__(f"SSL error for {url}: {error}")
        self.url = url
        self.error = error

    def to_dict(self) -> Dict:
        return {
            "url": self.url,
            "error": self.error,
            "type": "ssl_error"
        }

class TimeoutError(CaptureError):
    """Exception raised when request times out."""
    def __init__(self, url: str, timeout: int):
        super().__init__(f"Request timed out after {timeout} seconds for {url}")
        self.url = url
        self.timeout = timeout

    def to_dict(self) -> Dict:
        return {
            "url": self.url,
            "timeout": self.timeout,
            "type": "timeout_error"
        }

class ConfigurationError(CaptureError):
    """Exception raised when configuration is invalid."""
    def __init__(self, error: str):
        super().__init__(f"Configuration error: {error}")
        self.error = error

    def to_dict(self) -> Dict:
        return {
            "error": self.error,
            "type": "configuration_error"
        }

@dataclass
class TreeNode:
    """Represents a node in the HTTP request tree structure."""
    url: str
    referer: Optional[str] = None
    children: List['TreeNode'] = field(default_factory=list)
    size: Optional[int] = None
    content_length: Optional[int] = None
    hash: Optional[str] = None
    status: Optional[int] = None
    is_redirect: bool = False
    redirect_chain: List[str] = field(default_factory=list)

    def to_dict(self, visited: Optional[Set[str]] = None) -> Dict:
        """
        Convert the node and its children to a dictionary representation.
        
        Args:
            visited: Set of visited URLs to prevent cycles
            
        Returns:
            Dict: Dictionary representation of the node
        """
        if visited is None:
            visited = set()
            
        # If we've seen this URL before, return a simplified representation
        if self.url in visited:
            return {
                "url": self.url,
                "is_cycle": True
            }
            
        visited.add(self.url)
        
        result = {
            "url": self.url,
            "referer": self.referer,
            "size": self.size,
            "content_length": self.content_length,
            "hash": self.hash,
            "status": self.status,
            "is_redirect": self.is_redirect,
            "redirect_chain": self.redirect_chain,
            "children": []
        }
        
        # Process children while maintaining cycle detection
        for child in self.children:
            child_dict = child.to_dict(visited.copy())
            result["children"].append(child_dict)
            
        return result

class ContentProcessor:
    """Handles content processing operations."""
    
    @staticmethod
    def calculate_hash_and_size(content: str, encoding: Optional[str]) -> tuple[Optional[str], Optional[int]]:
        """Calculate content hash and size."""
        if not content:
            return None, None

        try:
            content_bytes = (base64.b64decode(content) if encoding == "base64" 
                           else content.encode("utf-8"))
            return hashlib.sha256(content_bytes).hexdigest(), len(content_bytes)
        except Exception:
            return None, None

class HARParser:
    """Parses HAR data into a tree structure."""

    @staticmethod
    def parse_to_tree(har_data: Dict) -> List[TreeNode]:
        """Parse HAR data into a tree structure."""
        if not har_data.get("log", {}).get("entries"):
            return []

        url_to_node: Dict[str, TreeNode] = {}
        root_nodes: List[TreeNode] = []
        referer_map: Dict[str, str] = {}
        redirect_map: Dict[str, str] = {}

        try:
            for entry in har_data["log"]["entries"]:
                node = HARParser._process_entry(entry, url_to_node)
                if node is None:
                    continue
                    
                if node.referer:
                    referer_map[node.url] = node.referer
                if node.is_redirect and node.redirect_chain:
                    redirect_map[node.url] = node.redirect_chain[0]

            HARParser._build_relationships(url_to_node, redirect_map, referer_map, root_nodes)
            
            return root_nodes if root_nodes else []

        except KeyError:
            return []
        except Exception:
            return []

    @staticmethod
    def _process_entry(entry: Dict, url_to_node: Dict[str, TreeNode]) -> Optional[TreeNode]:
        """Process a single HAR entry."""
        try:
            request = entry["request"]
            response = entry["response"]
            url = request["url"]
            
            headers = {
                header["name"].lower(): header["value"]
                for header in request.get("headers", [])
            }
            response_headers = {
                header["name"].lower(): header["value"]
                for header in response.get("headers", [])
            }

            node = url_to_node.get(url)
            if not node:
                node = TreeNode(url=url, referer=headers.get("referer"))
                url_to_node[url] = node

            content = response.get("content", {})
            content_hash, content_size = ContentProcessor.calculate_hash_and_size(
                content.get("text", ""),
                content.get("encoding")
            )

            node.size = content_size
            node.content_length = int(response_headers.get("content-length", 0)) or None
            node.hash = content_hash
            node.status = response.get("status", 0)

            if node.status in {301, 302, 303, 307, 308}:
                location = response_headers.get("location")
                if location:
                    node.is_redirect = True
                    node.redirect_chain.append(location)

            return node

        except (KeyError, Exception):
            return None

    @staticmethod
    def _build_relationships(
        url_to_node: Dict[str, TreeNode],
        redirect_map: Dict[str, str],
        referer_map: Dict[str, str],
        root_nodes: List[TreeNode]
    ) -> None:
        """Build parent-child relationships between nodes."""
        visited = set()
        processed = set()

        for url, node in url_to_node.items():
            if url in processed:
                continue
                
            current = node
            redirect_chain = set()

            # Handle redirect chains
            while current.url in redirect_map and current.url not in redirect_chain:
                redirect_chain.add(current.url)
                redirect_url = redirect_map[current.url]
                
                if redirect_url in url_to_node:
                    parent_node = url_to_node[redirect_url]
                    if parent_node not in current.children:
                        parent_node.children.append(current)
                    current = parent_node
                else:
                    break

            # Handle referer relationships
            if current.url not in visited:
                parent_url = referer_map.get(current.url)
                if parent_url and parent_url in url_to_node:
                    parent_node = url_to_node[parent_url]
                    if current not in parent_node.children:
                        parent_node.children.append(current)
                elif current not in root_nodes:
                    root_nodes.append(current)
                    
                visited.add(current.url)
            
            processed.add(url)

def validate_config(config: Dict) -> bool:
    """Validate capture configuration."""
    if not config.get("url"):
        raise ConfigurationError("URL is required")
    
    try:
        parsed_url = urlparse(config["url"])
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise ConfigurationError("Invalid URL format")
    except Exception as e:
        raise ConfigurationError(f"URL parsing error: {str(e)}")

    if config.get("proxy_list"):
        for proxy in config["proxy_list"]:
            try:
                parsed_proxy = urlparse(proxy)
                if not all([parsed_proxy.scheme, parsed_proxy.netloc]):
                    raise ConfigurationError(f"Invalid proxy format: {proxy}")
            except Exception as e:
                raise ConfigurationError(f"Proxy parsing error: {str(e)}")
    return True

async def try_capture_with_proxy(capture, config: Dict, proxy: str) -> Dict:
    """Attempt capture with a specific proxy."""
    try:
        if config.get("user_agent"):
            capture.user_agent = config.get("user_agent")

        await capture.initialize_context()
        
        entries = await capture.capture_page(
            config["url"],
            max_depth_capture_time=90
        )
        if entries.get('error'):
            if "SSL" in str(entries.get('error')):
                raise SSLError(config["url"], str(entries.get('error')))
            raise CaptureError(f"Capture error: {entries.get('error_name', 'Unknown error')}")

        return entries

    except Exception as e:
        if "ssl" in str(e).lower():
            raise SSLError(config["url"], str(e))
        elif "timed_out" in str(e).lower():
            raise TimeoutError(config["url"], config.get("max_time", 90))
        elif "proxy" in str(e).lower():
            raise ProxyError(proxy, str(e))
        raise CaptureError(f"Playwright error: {str(e)}")

async def capture_and_analyze(config: Dict) -> Dict:
    """Capture and analyze HTTP traffic with proxy support and error handling."""
    validate_config(config)
    start_time = time.time()
    from playwrightcapture import Capture

    proxy_list = config.get("proxy_list", [])
    last_error = None
    entries = None

    # If no proxies, try direct connection
    if not proxy_list:
        async with Capture() as capture:
            try:
                entries = await try_capture_with_proxy(capture, config, None)
                
            except SSLError:
                # Retry without SSL verification
                config["verify_ssl"] = False
                entries = await try_capture_with_proxy(capture, config, None)
                
    else:
        # Try each proxy in the list
        for proxy in proxy_list:
            try:
                async with Capture(proxy=proxy) as capture:
                    try:
                        entries = await try_capture_with_proxy(capture, config, proxy)
                        break
                    except SSLError:
                        # Retry current proxy without SSL verification
                        config["verify_ssl"] = False
                        try:
                            entries = await try_capture_with_proxy(capture, config, proxy)
                            break
                        except Exception as e:
                            last_error = e
                            continue
                    except Exception as e:
                        last_error = e
                        continue
            except Exception as e:
                last_error = e
                continue
        else:
            if last_error:
                raise last_error
            raise CaptureError("All proxies failed")

    if entries is None:
        raise CaptureError("Capture failed - no valid entries data")
    
    tree = HARParser.parse_to_tree(entries['har'])
    if not tree:
        raise CaptureError("Failed to parse HAR data into tree structure")
        
    screenshot = None
    if entries.get("png"):
        if isinstance(entries["png"], bytes):
            screenshot = base64.b64encode(entries["png"]).decode('utf-8')
        else:
            screenshot = entries["png"]
            
    elapsed_time = time.time() - start_time
    
    return {
        'url': config['url'],
        'capture_time': elapsed_time,
        'tree': [node.to_dict() for node in tree],
        "last_redirected_url": entries["last_redirected_url"],
        "title": entries.get('har', {}).get('log', {}).get('pages', [{}])[0].get('title', ''),
        "screenshot": screenshot
    }
