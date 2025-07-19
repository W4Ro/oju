"""
HAR Tree Difference Analyzer

This module provides functionality to analyze differences between two HAR trees,
with visual tree representation and comprehensive change detection.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from asgiref.sync import sync_to_async
from enum import Enum
from urllib.parse import urlparse
from django.core.cache import cache
import logging
from core.definitions import *

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 12 * 60 * 60

class ChangeType(Enum):
    """Types of changes that can occur in the HAR tree."""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    MOVED = "moved"
    CONTENT_CHANGED = "content_changed"
    STATUS_CHANGED = "status_changed"
    SIZE_CHANGED = "size_changed"
    TITLE_CHANGED = "title_changed"
    REDIRECT_CHANGED = "redirect_changed"
    METADATA_CHANGED = "metadata_changed"

@dataclass
class Change:
    """Represents a change between two versions of a node."""
    type: ChangeType
    url: str
    old_value: Optional[dict] = None
    new_value: Optional[dict] = None
    details: Optional[str] = None
    path: Optional[List[str]] = None


def get_size_tolerance_sync():
    """
    Get SIZE_TOLERANCE from cache or database.
    """
    
    tolerance = cache.get(SIZE_TOLERANCE_CACHE_KEY)
    
    if tolerance is None:
        from .models import DefacementScanCriteria
        try:
            
            criteria = DefacementScanCriteria.objects.first()
            tolerance = criteria.acceptance_rate if criteria else 100 
        except Exception as e:
            logger.warning(f"Error fetching SIZE_TOLERANCE from DB: {e}")
            tolerance = 100  # Default fallback
        
        # Store in cache
        cache.set(SIZE_TOLERANCE_CACHE_KEY, tolerance, CACHE_TIMEOUT)
    
    return tolerance

def get_whitelist_domains_sync():
    """
    Get WHITELIST_DOMAINS from cache or database.
    """
    domains = cache.get(WHITELIST_DOMAINS_CACHE_KEY)
    
    if domains is None:
        from .models import DefacementScanCriteria, WhitelistedDomain
        domains = []
        try:
            criteria = DefacementScanCriteria.objects.first()
            if criteria:
                domain_object = WhitelistedDomain.objects.filter(defacement_criteria=criteria)
                domains = [domain_obj.domain for domain_obj in domain_object]
        except Exception as e:
            logger.warning(f"Error fetching WHITELIST_DOMAINS from DB: {e}")
            # Default fallback already set
        
        # Store in cache
        cache.set(WHITELIST_DOMAINS_CACHE_KEY, domains, CACHE_TIMEOUT)
    
    return domains

get_size_tolerance = sync_to_async(get_size_tolerance_sync)
get_whitelist_domains = sync_to_async(get_whitelist_domains_sync)

class TreeDiffer:
    """Analyzes differences between two HAR trees."""
    
    def __init__(self, old_capture: dict, new_capture: dict, size_tolerance: int = 100, whitelist_domains: List[str] = None) -> None:
        """Initialize with two HAR captures to compare."""
        self.old_capture = old_capture
        self.new_capture = new_capture
        self.old_tree = old_capture.get("tree", [])
        self.new_tree = new_capture.get("tree", [])
        self.changes: List[Change] = []
        self.SIZE_TOLERANCE = size_tolerance
        self.WHITELIST_DOMAINS = set(whitelist_domains or [])  # Convert to set for O(1) lookup

        # Caches for nodes and paths
        self.old_nodes: Dict[str, dict] = {}
        self.new_nodes: Dict[str, dict] = {}
        self.old_paths: Dict[str, List[str]] = {}
        self.new_paths: Dict[str, List[str]] = {}
        self.node_domains: Dict[str, Set[str]] = {}
        
        self._build_caches()

    def _normalize_url(self, url: str) -> str:
        """Remove query parameters and fragments from URL."""
        try:
            parsed = urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        except Exception:
            return url  # Fallback if URL is malformed

    def _is_legitimate_domain(self, url: str) -> bool:
        """Check if a URL belongs to a whitelisted domain (exact match)."""
        try:
            domain = urlparse(url).netloc
            return domain in self.WHITELIST_DOMAINS
        except:
            return False

    def _is_font_file(self, url: str) -> bool:
        """Return True if the URL is a font file."""
        try:
            parsed_url = urlparse(url)
            path = parsed_url.path
            filename = path.split('/')[-1]
            extension = ''
            if '.' in filename:
                extension = filename.split('.')[-1]
            if extension in ['woff2', 'woff', 'ttf', 'eot', 'otf']:
                return True
            
            return False
                
        except Exception as e:
            return False

    def _is_ignorable_blob(self, url: str, parent_url: str = None) -> bool:
        """
        Check if a URL is a blob URL.
        Returns True if the URL is ignorable (not suspicious).
        """
        try:
            if not url.startswith("blob:"):
                return False
            
            if not parent_url:
                return False
                
            # Extract the actual URL from blob:https://domain.com/uuid
            actual_url = url[5:]  # Remove "blob:"
            parsed_actual_url = urlparse(actual_url)
            parsed_parent_url = urlparse(parent_url)
            
            return parsed_actual_url.netloc == parsed_parent_url.netloc
        except Exception as e:
            return False

    def _should_report_change(self, url: str, parent_url: Optional[str] = None) -> bool:
        """
        Determine if a change should be reported based on domain legitimacy rules, 
        font file checks, and blob URL checks.
        Returns True if the change should be reported (suspicious).
        """
        # Always ignore whitelisted domains completely
        if self._is_legitimate_domain(url):
            return False
            
        if self._is_font_file(url):
            return False
        
        if self._is_ignorable_blob(url, parent_url):
            return False
                
        return True

    def _build_caches(self) -> None:
        """Build URL-to-node and path caches for both trees."""
        def process_tree(tree: List[dict], nodes: Dict[str, dict], 
                        paths: Dict[str, List[str]], 
                        current_path: List[str] = None,
                        parent_url: Optional[str] = None) -> None:
            if current_path is None:
                current_path = []
                
            for node in tree:
                url = node["url"]
                nodes[url] = node
                paths[url] = current_path + [url]
                
                # Cache domains for this node
                if parent_url:
                    if parent_url not in self.node_domains:
                        self.node_domains[parent_url] = set()
                    try:
                        domain = urlparse(url).netloc.lower()
                        self.node_domains[parent_url].add(domain)
                    except:
                        pass
                
                if node.get("children"):
                    process_tree(node["children"], nodes, paths, paths[url], url)
        
        process_tree(self.old_tree, self.old_nodes, self.old_paths)
        process_tree(self.new_tree, self.new_nodes, self.new_paths)

    def _build_parent_children_map(self, tree: List[dict]) -> Dict[str, List[dict]]:
        """Build mapping of normalized parent URL -> list of children."""
        parent_children = {}
        
        def process_node(node: dict, parent_url: str = None):
            url = node["url"]
            
            # If root node, use "root" as parent identifier
            if parent_url is None:
                parent_key = "root"
            else:
                parent_key = self._normalize_url(parent_url)
                
            if parent_key not in parent_children:
                parent_children[parent_key] = []
            parent_children[parent_key].append(node)
            
            # Process children recursively
            for child in node.get("children", []):
                process_node(child, url)
        
        for root_node in tree:
            process_node(root_node)
        
        return parent_children

    def _compare_node_content(self, old_node: dict, new_node: dict, parent_url: Optional[str] = None) -> List[Change]:
        """Compare content-related attributes of two nodes."""
        changes = []
        url = old_node["url"]
        
        if not self._should_report_change(url, parent_url):
            return changes
            
        path = self.new_paths.get(url, self.old_paths.get(url, []))

        # Compare sizes with tolerance
        old_size = old_node.get("size")
        new_size = new_node.get("size")
        size_diff = -1
        if old_size is not None and new_size is not None:
            size_diff = abs(new_size - old_size)
            if size_diff > self.SIZE_TOLERANCE:
                changes.append(Change(
                    type=ChangeType.SIZE_CHANGED,
                    url=url,
                    old_value={"size": old_size},
                    new_value={"size": new_size},
                    details=f"Size changed from {old_size} to {new_size} bytes (diff: {size_diff} bytes)",
                    path=path
                ))

        # Compare hashes with same size
        old_hash = old_node.get("hash")
        new_hash = new_node.get("hash")
        # if old_hash != new_hash:
        #     if size_diff == 0:
        #         changes.append(Change(
        #             type=ChangeType.CONTENT_CHANGED,
        #             url=url,
        #             old_value={"hash": old_hash},
        #             new_value={"hash": new_hash},
        #             details="Content changed but size is same (possible suspicious change)",
        #             path=path
        #         ))

        # Compare status codes
        old_status = old_node.get("status")
        new_status = new_node.get("status")
        if old_status != new_status and old_status is not None and new_status is not None and old_status != -1 and new_status != -1:
            changes.append(Change(
                type=ChangeType.STATUS_CHANGED,
                url=url,
                old_value={"status": old_status},
                new_value={"status": new_status},
                details=f"Status changed from {old_status} to {new_status}",
                path=path
            ))

        return changes

    def _compare_parent_children(self, parent_key: str, old_children: List[dict], new_children: List[dict]):
        """Compare children of the same parent between old and new trees."""
        
        # Get actual parent URL for reporting and blob checking
        if parent_key == "root":
            # For root nodes, use the main capture URL as parent for blob checking
            parent_url = self.new_capture.get("url")
        else:
            parent_url = parent_key
        
        # Create mappings of normalized URL -> node for quick lookup
        old_normalized = {}
        new_normalized = {}
        
        for child in old_children:
            norm_url = self._normalize_url(child["url"])
            old_normalized[norm_url] = child
            
        for child in new_children:
            norm_url = self._normalize_url(child["url"])
            new_normalized[norm_url] = child
        
        # Detect additions (new normalized URLs)
        for norm_url, child in new_normalized.items():
            if norm_url not in old_normalized:
                if self._should_report_change(child["url"], parent_url):
                    self.changes.append(Change(
                        type=ChangeType.ADDED,
                        url=child["url"],
                        new_value=child,
                        path=self.new_paths.get(child["url"], [])
                    ))
        
        # Detect removals (old normalized URLs not in new)
        for norm_url, child in old_normalized.items():
            if norm_url not in new_normalized:
                if self._should_report_change(child["url"], parent_url):
                    self.changes.append(Change(
                        type=ChangeType.REMOVED,
                        url=child["url"],
                        old_value=child,
                        path=self.old_paths.get(child["url"], [])
                    ))
        
        # Detect modifications (same normalized URL, potentially different actual URL or content)
        for norm_url in old_normalized.keys() & new_normalized.keys():
            old_child = old_normalized[norm_url]
            new_child = new_normalized[norm_url]
            
            # Compare content even if URLs are identical
            self.changes.extend(
                self._compare_node_content(old_child, new_child, parent_url)
            )

    def _detect_moved_resources(self) -> None:
        """Detect resources that moved from one parent to another."""
        for url in self.old_nodes:
            if url in self.new_nodes:
                old_path = self.old_paths.get(url)
                new_path = self.new_paths.get(url)
                if old_path and new_path and old_path != new_path:
                    if self._should_report_change(url):
                        self.changes.append(Change(
                            type=ChangeType.MOVED,
                            url=url,
                            old_value={"path": old_path},
                            new_value={"path": new_path},
                            details="Resource moved within the tree",
                            path=new_path
                        ))

    def _detect_structural_changes(self) -> None:
        """Detect structural changes by comparing parent by parent."""
        
        # Build parent-children mappings for both trees
        old_parent_children = self._build_parent_children_map(self.old_tree)
        new_parent_children = self._build_parent_children_map(self.new_tree)
        
        # Get all parent keys from both trees
        all_parent_keys = set(old_parent_children.keys()) | set(new_parent_children.keys())
        
        # Compare each parent and its children
        for parent_key in all_parent_keys:
            old_children = old_parent_children.get(parent_key, [])
            new_children = new_parent_children.get(parent_key, [])
            
            if not old_children:
                # New parent with children - report all as added
                for child in new_children:
                    parent_url = self.new_capture.get("url") if parent_key == "root" else parent_key
                    if self._should_report_change(child["url"], parent_url):
                        self.changes.append(Change(
                            type=ChangeType.ADDED,
                            url=child["url"],
                            new_value=child,
                            path=self.new_paths.get(child["url"], [])
                        ))
            elif not new_children:
                # Removed parent with children - report all as removed
                for child in old_children:
                    parent_url = self.old_capture.get("url") if parent_key == "root" else parent_key
                    if self._should_report_change(child["url"], parent_url):
                        self.changes.append(Change(
                            type=ChangeType.REMOVED,
                            url=child["url"],
                            old_value=child,
                            path=self.old_paths.get(child["url"], [])
                        ))
            else:
                # Both parents exist - compare their children
                self._compare_parent_children(parent_key, old_children, new_children)
        
        # Detect moved resources separately
        # self._detect_moved_resources()

    def _compare_metadata(self) -> None:
        """Compare title and redirect URL changes."""
        # Compare titles
        old_title = self.old_capture.get("title", "")
        new_title = self.new_capture.get("title", "")
        if old_title != new_title:
            self.changes.append(Change(
                type=ChangeType.TITLE_CHANGED,
                url="",
                old_value={"title": old_title},
                new_value={"title": new_title},
                details=f"Page title changed from '{old_title}' to '{new_title}'"
            ))

        # Compare redirect URLs
        old_redirect = self.old_capture.get("last_redirected_url", "")
        new_redirect = self.new_capture.get("last_redirected_url", "")
        if old_redirect != new_redirect:
            self.changes.append(Change(
                type=ChangeType.REDIRECT_CHANGED,
                url="",
                old_value={"redirect": old_redirect},
                new_value={"redirect": new_redirect},
                details=f"Final redirect changed from '{old_redirect}' to '{new_redirect}'"
            ))

    def analyze(self) -> List[Change]:
        """Analyze differences between the two trees."""
        self._compare_metadata()
        self._detect_structural_changes()
        return self.changes

def visualize_tree(tree: List[dict], indent: str = "", is_last: bool = True) -> str:
    """Create a visual representation of the tree structure."""
    result = []
    
    for i, node in enumerate(tree):
        is_current_last = i == len(tree) - 1
        prefix = indent + ("└── " if is_current_last else "├── ")
        
        result.append(f"{prefix}{node['url']}")
        
        if node.get("children"):
            new_indent = indent + ("    " if is_current_last else "│   ")
            result.append(visualize_tree(node["children"], new_indent, is_current_last))
    
    return "\n".join(result)

def format_changes(changes: List[Change], old_tree: List[dict], new_tree: List[dict]) -> str:
    """Format changes into a human-readable string with tree visualization."""
    if not changes:
        return None

    formatted = ["Changes detected:\n"]
    
    # Group changes by type
    metadata_changes = []
    structural_changes = []
    content_changes = []
    
    for change in changes:
        if change.type in {ChangeType.TITLE_CHANGED, ChangeType.REDIRECT_CHANGED}:
            metadata_changes.append(change)
        elif change.type in {ChangeType.ADDED, ChangeType.REMOVED, ChangeType.MOVED}:
            structural_changes.append(change)
        else:
            content_changes.append(change)

    # Format metadata changes
    if metadata_changes:
        formatted.append("Metadata Changes:")
        for change in metadata_changes:
            formatted.append(f"  • {change.details}")
        formatted.append("")

    # Format structural changes with path
    if structural_changes:
        formatted.append("Structural Changes:")
        for change in structural_changes:
            path_str = " → ".join(change.path) if change.path else "root"
            if change.type == ChangeType.ADDED:
                formatted.append(f"  ➕ Added: {change.url}")
                formatted.append(f"     Path: {path_str}")
            elif change.type == ChangeType.REMOVED:
                formatted.append(f"  ❌ Removed: {change.url}")
                formatted.append(f"     Path: {path_str}")
            elif change.type == ChangeType.MOVED:
                formatted.append(f"   Moved: {change.url}")
                formatted.append(f"     Old path: {' → '.join(change.old_value['path'])}")
                formatted.append(f"     New path: {' → '.join(change.new_value['path'])}")
        formatted.append("")

    # Format content changes with path
    if content_changes:
        formatted.append("Content Changes:")
        for change in content_changes:
            path_str = " → ".join(change.path) if change.path else "root"
            if change.type == ChangeType.CONTENT_CHANGED:
                formatted.append(f"   Content changed: {change.url}")
                formatted.append(f"     Path: {path_str}")
                if change.details:
                    formatted.append(f"     Details: {change.details}")
            elif change.type == ChangeType.STATUS_CHANGED:
                formatted.append(f"   Status: {change.details}")
                formatted.append(f"     Path: {path_str}")
            elif change.type == ChangeType.SIZE_CHANGED:
                formatted.append(f"   Size: {change.details}")
                formatted.append(f"     Path: {path_str}")
        formatted.append("")

    return "\n".join(formatted)

async def compare_captures(old_capture: dict, new_capture: dict) -> str:
    """Compare two HAR captures and return formatted changes with tree visualization."""
    size_tolerance = await get_size_tolerance()
    whitelist_domains = await get_whitelist_domains()
    differ = TreeDiffer(old_capture, new_capture, size_tolerance, whitelist_domains)

    changes = differ.analyze()
    return format_changes(changes, old_capture.get("tree", []), new_capture.get("tree", []))