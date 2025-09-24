"""
Azure DevOps MCP Server - API Client
"""

import os
import base64
from typing import List, Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3

from config import (
    DISABLE_SSL_VERIFY, REQUEST_TIMEOUT, RETRY_TOTAL, RETRY_BACKOFF_FACTOR,
    RETRY_STATUS_FORCELIST, API_VERSION, WIQL_API_VERSION
)

# Disable SSL warnings if verification is disabled (debugging only)
if DISABLE_SSL_VERIFY:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AzureDevOpsClient:
    """Azure DevOps REST API client using requests"""
    
    def __init__(self, organization: str, project: str, pat: str):
        self.organization = organization
        self.project = project
        self.base_url = f"https://dev.azure.com/{organization}"
        
        # Create session with proper configuration
        self.session = requests.Session()
        
        # Authentication
        auth_string = f":{pat}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        self.session.headers.update({
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json',
            'User-Agent': 'Azure-DevOps-MCP-Server/1.0'
        })
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=RETRY_TOTAL,
            backoff_factor=RETRY_BACKOFF_FACTOR,
            status_forcelist=RETRY_STATUS_FORCELIST,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # SSL Configuration
        self._configure_ssl()
        
        # Set timeout
        self.timeout = REQUEST_TIMEOUT
    
    def _configure_ssl(self):
        """Configure SSL verification"""
        # Option 1: Disable SSL verification for debugging (INSECURE!)
        if DISABLE_SSL_VERIFY:
            self.session.verify = False
            # Don't print to stdout in MCP server - it breaks JSON-RPC protocol
            return
        
        # Option 2: Use custom certificate bundle
        cert_file = os.getenv("SSL_CERT_FILE") or os.getenv("REQUESTS_CA_BUNDLE") or os.getenv("CURL_CA_BUNDLE")
        if cert_file and os.path.exists(cert_file):
            self.session.verify = cert_file
            return
        
        # Option 3: Try to use certifi bundle
        try:
            import certifi
            self.session.verify = certifi.where()
        except ImportError:
            # requests will use system default certificates
            pass
    
    def get_work_items(self, work_item_type: str = "User Story", top: int = 100) -> List[Dict[str, Any]]:
        """Fetch work items from Azure DevOps"""
        
        try:
            # WIQL query to get work items
            query = {
                "query": f"""
                SELECT [System.Id], [System.Title], [System.WorkItemType], 
                       [System.State], [System.AssignedTo], [System.AreaPath],
                       [System.IterationPath], [System.Description], 
                       [System.CreatedDate], [System.ChangedDate], [System.Tags],
                       [Microsoft.VSTS.TCM.Steps], [Microsoft.VSTS.Common.Priority],
                       [Microsoft.VSTS.TCM.AutomationStatus]
                FROM workitems 
                WHERE [System.TeamProject] = '{self.project}' 
                    AND [System.WorkItemType] = '{work_item_type}'
                ORDER BY [System.ChangedDate] DESC
                """
            }
            
            # Execute WIQL query
            wiql_url = f"{self.base_url}/{self.project}/_apis/wit/wiql?api-version={WIQL_API_VERSION}"
            
            response = self.session.post(wiql_url, json=query, timeout=self.timeout)
            response.raise_for_status()
            
            wiql_result = response.json()
            work_item_ids = [item["id"] for item in wiql_result.get("workItems", [])]
            
            if not work_item_ids:
                return []
            
            # Limit the number of IDs if necessary
            work_item_ids = work_item_ids[:top]
            
            # Get full work item details
            ids_param = ",".join(map(str, work_item_ids))
            details_url = f"{self.base_url}/{self.project}/_apis/wit/workitems"
            params = {
                "ids": ids_param,
                "api-version": API_VERSION,
                "$expand": "fields"
            }
            
            details_response = self.session.get(details_url, params=params, timeout=self.timeout)
            details_response.raise_for_status()
            
            details_result = details_response.json()
            return details_result.get("value", [])
            
        except requests.exceptions.SSLError as e:
            raise Exception(f"SSL Error: {str(e)}. Try installing/updating certificates or set AZURE_DEVOPS_DISABLE_SSL_VERIFY=true for debugging (insecure)")
        except requests.exceptions.ProxyError as e:
            raise Exception(f"Proxy Error: {str(e)}. Check your proxy settings (HTTP_PROXY, HTTPS_PROXY)")
        except requests.exceptions.ConnectionError as e:
            raise Exception(f"Connection Error: {str(e)}. Check your network connection")
        except requests.exceptions.Timeout:
            raise Exception(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"HTTP Error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
    
    def get_work_item_by_id(self, work_item_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a specific work item by ID"""
        
        try:
            url = f"{self.base_url}/{self.project}/_apis/wit/workitems/{work_item_id}"
            params = {"api-version": API_VERSION, "$expand": "fields"}
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.SSLError as e:
            raise Exception(f"SSL Error: {str(e)}. Try installing/updating certificates or set AZURE_DEVOPS_DISABLE_SSL_VERIFY=true for debugging (insecure)")
        except requests.exceptions.ProxyError as e:
            raise Exception(f"Proxy Error: {str(e)}. Check your proxy settings")
        except requests.exceptions.ConnectionError as e:
            raise Exception(f"Connection Error: {str(e)}. Check your network connection")
        except requests.exceptions.Timeout:
            raise Exception(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise Exception(f"HTTP Error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
    
    def update_work_item(self, work_item_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a work item with specified field values"""
        
        try:
            # Prepare the patch document
            patch_operations = []
            for field_path, value in updates.items():
                patch_operations.append({
                    "op": "replace",
                    "path": f"/fields/{field_path}",
                    "value": value
                })
            
            url = f"{self.base_url}/{self.project}/_apis/wit/workitems/{work_item_id}"
            params = {"api-version": API_VERSION}
            
            # Update content type for PATCH operations
            headers = self.session.headers.copy()
            headers["Content-Type"] = "application/json-patch+json"
            
            response = self.session.patch(
                url, 
                json=patch_operations, 
                params=params, 
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 404:
                raise Exception(f"Work item {work_item_id} not found")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.SSLError as e:
            raise Exception(f"SSL Error: {str(e)}. Try installing/updating certificates or set AZURE_DEVOPS_DISABLE_SSL_VERIFY=true for debugging (insecure)")
        except requests.exceptions.ProxyError as e:
            raise Exception(f"Proxy Error: {str(e)}. Check your proxy settings")
        except requests.exceptions.ConnectionError as e:
            raise Exception(f"Connection Error: {str(e)}. Check your network connection")
        except requests.exceptions.Timeout:
            raise Exception(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"HTTP Error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
    
    def search_work_items_by_title(self, search_term: str, work_item_type: str = "User Story", top: int = 50) -> List[Dict[str, Any]]:
        """Search work items by title"""
        
        try:
            # WIQL query to search work items by title
            query = {
                "query": f"""
                SELECT [System.Id], [System.Title], [System.WorkItemType], 
                       [System.State], [System.AssignedTo], [System.AreaPath],
                       [System.IterationPath], [System.Description], 
                       [System.CreatedDate], [System.ChangedDate], [System.Tags],
                       [Microsoft.VSTS.TCM.Steps], [Microsoft.VSTS.Common.Priority],
                       [Microsoft.VSTS.TCM.AutomationStatus]
                FROM workitems 
                WHERE [System.TeamProject] = '{self.project}' 
                    AND [System.WorkItemType] = '{work_item_type}'
                    AND [System.Title] CONTAINS '{search_term}'
                ORDER BY [System.ChangedDate] DESC
                """
            }
            
            # Execute WIQL query
            wiql_url = f"{self.base_url}/{self.project}/_apis/wit/wiql?api-version={WIQL_API_VERSION}"
            
            response = self.session.post(wiql_url, json=query, timeout=self.timeout)
            response.raise_for_status()
            
            wiql_result = response.json()
            work_item_ids = [item["id"] for item in wiql_result.get("workItems", [])]
            
            if not work_item_ids:
                return []
            
            # Limit the number of IDs if necessary
            work_item_ids = work_item_ids[:top]
            
            # Get full work item details
            ids_param = ",".join(map(str, work_item_ids))
            details_url = f"{self.base_url}/{self.project}/_apis/wit/workitems"
            params = {
                "ids": ids_param,
                "api-version": API_VERSION,
                "$expand": "fields"
            }
            
            details_response = self.session.get(details_url, params=params, timeout=self.timeout)
            details_response.raise_for_status()
            
            details_result = details_response.json()
            return details_result.get("value", [])
            
        except requests.exceptions.SSLError as e:
            raise Exception(f"SSL Error: {str(e)}. Try installing/updating certificates or set AZURE_DEVOPS_DISABLE_SSL_VERIFY=true for debugging (insecure)")
        except requests.exceptions.ProxyError as e:
            raise Exception(f"Proxy Error: {str(e)}. Check your proxy settings")
        except requests.exceptions.ConnectionError as e:
            raise Exception(f"Connection Error: {str(e)}. Check your network connection")
        except requests.exceptions.Timeout:
            raise Exception(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"HTTP Error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
    
    def create_work_item(self, work_item_type: str, title: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new work item in Azure DevOps"""
        
        try:
            # Prepare the patch document for creation
            patch_operations = [
                {
                    "op": "add",
                    "path": "/fields/System.Title",
                    "value": title
                },
                {
                    "op": "add", 
                    "path": "/fields/System.WorkItemType",
                    "value": work_item_type
                }
            ]
            
            # Add additional fields
            for field_path, value in fields.items():
                if value is not None:  # Only add non-None values
                    patch_operations.append({
                        "op": "add",
                        "path": f"/fields/{field_path}",
                        "value": value
                    })
            
            url = f"{self.base_url}/{self.project}/_apis/wit/workitems/${work_item_type}"
            params = {"api-version": API_VERSION}
            
            # Update content type for PATCH operations
            headers = self.session.headers.copy()
            headers["Content-Type"] = "application/json-patch+json"
            
            response = self.session.post(
                url, 
                json=patch_operations, 
                params=params, 
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.SSLError as e:
            raise Exception(f"SSL Error: {str(e)}. Try installing/updating certificates or set AZURE_DEVOPS_DISABLE_SSL_VERIFY=true for debugging (insecure)")
        except requests.exceptions.ProxyError as e:
            raise Exception(f"Proxy Error: {str(e)}. Check your proxy settings")
        except requests.exceptions.ConnectionError as e:
            raise Exception(f"Connection Error: {str(e)}. Check your network connection")
        except requests.exceptions.Timeout:
            raise Exception(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"HTTP Error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")

    def get_work_items_by_state(self, state: str, work_item_type: str = "User Story", top: int = 100) -> List[Dict[str, Any]]:
        """Get work items filtered by state"""
        
        try:
            # WIQL query to get work items by state
            query = {
                "query": f"""
                SELECT [System.Id], [System.Title], [System.WorkItemType], 
                       [System.State], [System.AssignedTo], [System.AreaPath],
                       [System.IterationPath], [System.Description], 
                       [System.CreatedDate], [System.ChangedDate], [System.Tags],
                       [Microsoft.VSTS.TCM.Steps], [Microsoft.VSTS.Common.Priority],
                       [Microsoft.VSTS.TCM.AutomationStatus]
                FROM workitems 
                WHERE [System.TeamProject] = '{self.project}' 
                    AND [System.WorkItemType] = '{work_item_type}'
                    AND [System.State] = '{state}'
                ORDER BY [System.ChangedDate] DESC
                """
            }
            
            # Execute WIQL query
            wiql_url = f"{self.base_url}/{self.project}/_apis/wit/wiql?api-version={WIQL_API_VERSION}"
            
            response = self.session.post(wiql_url, json=query, timeout=self.timeout)
            response.raise_for_status()
            
            wiql_result = response.json()
            work_item_ids = [item["id"] for item in wiql_result.get("workItems", [])]
            
            if not work_item_ids:
                return []
            
            # Limit the number of IDs if necessary
            work_item_ids = work_item_ids[:top]
            
            # Get full work item details
            ids_param = ",".join(map(str, work_item_ids))
            details_url = f"{self.base_url}/{self.project}/_apis/wit/workitems"
            params = {
                "ids": ids_param,
                "api-version": API_VERSION,
                "$expand": "fields"
            }
            
            details_response = self.session.get(details_url, params=params, timeout=self.timeout)
            details_response.raise_for_status()
            
            details_result = details_response.json()
            return details_result.get("value", [])
            
        except requests.exceptions.SSLError as e:
            raise Exception(f"SSL Error: {str(e)}. Try installing/updating certificates or set AZURE_DEVOPS_DISABLE_SSL_VERIFY=true for debugging (insecure)")
        except requests.exceptions.ProxyError as e:
            raise Exception(f"Proxy Error: {str(e)}. Check your proxy settings")
        except requests.exceptions.ConnectionError as e:
            raise Exception(f"Connection Error: {str(e)}. Check your network connection")
        except requests.exceptions.Timeout:
            raise Exception(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"HTTP Error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")