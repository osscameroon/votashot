import requests
import urllib.parse
from threading import Lock
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class SessionManager:
    def __init__(self, max_pool_size=100, ttl_minutes=5, pool_connections=20, pool_maxsize=50):
        self.sessions = {}  # hostname -> (session, last_used_time)
        self.lock = Lock()
        self.max_pool_size = max_pool_size
        self.ttl = timedelta(minutes=ttl_minutes)
        self.pool_connections = pool_connections
        self.pool_maxsize = pool_maxsize
        self.last_cleanup = datetime.now()
        self.cleanup_interval = timedelta(seconds=30)

    def get_session(self, url):
        hostname = urllib.parse.urlparse(url).netloc

        with self.lock:
            now = datetime.now()
            # Clean up old sessions if needed
            if now - self.last_cleanup > self.cleanup_interval:
                self._cleanup_old_sessions()
                self.last_cleanup = now

            # Get or create session
            if hostname in self.sessions:
                session, _ = self.sessions[hostname]
                self.sessions[hostname] = (session, datetime.now())
            else:
                # Create new session with retry configuration
                session = requests.Session()
                retry_strategy = Retry(
                    total=3,
                    backoff_factor=0.3,
                    status_forcelist=[
                        408, 429, 502, 503, 504  # Common transient errors
                        # Consider adding provider-specific codes (e.g. 522, 524) only if relevant
                    ],
                    allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
                )
                adapter = HTTPAdapter(
                    max_retries=retry_strategy,
                    pool_connections=self.pool_connections,
                    pool_maxsize=self.pool_maxsize,
                )
                session.mount("http://", adapter)
                session.mount("https://", adapter)

                self.sessions[hostname] = (session, datetime.now())

            return self.sessions[hostname][0]

    def _cleanup_old_sessions(self):
        # Remove sessions that haven't been used recently
        now = datetime.now()
        expired_hosts = []

        # Find expired sessions
        for hostname, (_, last_used) in self.sessions.items():
            if now - last_used > self.ttl:
                expired_hosts.append(hostname)

        # Remove expired sessions
        for hostname in expired_hosts:
            del self.sessions[hostname]

        # If we're still over max pool size, remove oldest sessions
        if len(self.sessions) > self.max_pool_size:
            hosts_by_age = sorted(
                self.sessions.items(),
                key=lambda x: x[1][1],  # Sort by last_used time
            )
            for hostname, _ in hosts_by_age[: len(self.sessions) - self.max_pool_size]:
                del self.sessions[hostname]

# ⚠️ Caution: If you’re using this in a multithreaded context, avoid sharing session objects across threads. Consider enhancing the SessionManager to return thread-local sessions per hostname if needed.