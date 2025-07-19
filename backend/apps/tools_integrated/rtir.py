import requests
from requests.exceptions import RequestException
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
logger = logging.getLogger(__name__)

class RTIRClient:
    def __init__(self, base_url: str, username: str, password: str) -> None:
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.authenticated = False

    def authenticate(self) -> bool:
        """Authenticates the user and maintains the session."""
        login_url = f"{self.base_url}/REST/1.0/login"
        auth_data = {"user": self.username, "pass": self.password}
        
        try:
            response = self.session.post(login_url, data=auth_data, verify=False, timeout=5)
            response.raise_for_status()
        except RequestException as e:
            logger.error(f"Authentication request failed: {e}")
            return False
        if "200 Ok" in response.text:
            self.authenticated = True
            return True
        else:
            logger.error(f"Authentication failed: {response.text}")
            return False

    def create_ticket(
        self, queue: str, subject: str, content: str,
        requestors: Optional[List[str]] = None, cc: Optional[List[str]] = None,
        admin_cc: Optional[List[str]] = None, priority: str = "Normal",
        ip: Optional[str] = None, domain: Optional[str] = None,
        cve_id: Optional[str] = None, reporter_type: Optional[str] = None,
        customer: Optional[str] = None, status: str = "new", due_days: int = 7
    ) -> Dict[str, Any]:
        """Creates a detailed RTIR ticket."""
        if not self.authenticated and not self.authenticate():
            return {"error": "Authentication failed"}

        ticket_url = f"{self.base_url}/REST/1.0/ticket/new"
        priority_mapping = {"Low": 0, "Normal": 10, "High": 50, "Critical": 100}
        priority_value = priority_mapping.get(priority, 10)
        due_date = (datetime.now() + timedelta(days=due_days)).strftime("%Y-%m-%d %H:%M:%S")

        ticket_data = f"""id: new
Queue: {queue}
Subject: {subject}
Text: {content}
Priority: {priority_value}
Status: {status}
Due: {due_date}
How Reported: REST
        """
        
        if requestors:
            ticket_data += f"Requestor: {', '.join(requestors)}\n"
        if cc:
            ticket_data += f"Cc: {', '.join(cc)}\n"
        if admin_cc:
            ticket_data += f"AdminCc: {', '.join(admin_cc)}\n"
        if ip:
            ticket_data += f"CF-IP: {ip}\n"
        if domain:
            ticket_data += f"CF-Domain: {domain}\n"
        if cve_id:
            ticket_data += f"CF-CVE ID: {cve_id}\n"
        if reporter_type:
            ticket_data += f"CF-Reporter Type: {reporter_type}\n"
        if customer:
            ticket_data += f"CF-Customer: {customer}\n"

        try:
            response = self.session.post(ticket_url, data={"content": ticket_data}, timeout=10, verify=False) 
            response.raise_for_status()
        except RequestException as e:
            logger.error(f"Ticket creation request failed: {e}")
            return {"error": f"Ticket creation request failed: {e}"}
            
        logger.info(f"Ticket creation response: {response.text}")
        if "200 Ok" in response.text:
            return {"success": response.text.strip()}
        return {"error": response.text.strip()}


