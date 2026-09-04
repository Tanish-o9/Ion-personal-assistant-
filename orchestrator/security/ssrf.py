import socket
import ipaddress
from urllib.parse import urlparse
from orchestrator.observability import jarvis_logger

BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback IPv4
    ipaddress.ip_network("10.0.0.0/8"),       # Private Class A
    ipaddress.ip_network("172.16.0.0/12"),    # Private Class B
    ipaddress.ip_network("192.168.0.0/16"),   # Private Class C
    ipaddress.ip_network("169.254.0.0/16"),   # Link-Local / Cloud Metadata
    ipaddress.ip_network("::1/128"),          # Loopback IPv6
    ipaddress.ip_network("fc00::/7"),         # Unique Local IPv6
    ipaddress.ip_network("fe80::/10"),        # Link-Local IPv6
]

BLOCKED_HOSTNAMES = {"localhost", "localhost.localdomain", "metadata.google.internal", "169.254.169.254"}

class SSRFProtector:
    """
    Protects web_fetch and HTTP tools against Server-Side Request Forgery (SSRF).
    Blocks loopback, private networks, cloud metadata endpoints, and internal infrastructure.
    """
    @staticmethod
    def validate_url(url: str) -> str:
        if not url or not isinstance(url, str):
            raise ValueError("URL must be a non-empty string.")

        parsed = urlparse(url)
        if parsed.scheme.lower() not in {"http", "https"}:
            raise ValueError(f"Invalid URL scheme '{parsed.scheme}'. Only HTTP and HTTPS are permitted.")

        hostname = parsed.hostname
        if not hostname:
            raise ValueError("URL does not contain a valid hostname.")

        hostname_lowered = hostname.lower().strip()
        if hostname_lowered in BLOCKED_HOSTNAMES:
            jarvis_logger.warning("SSRF blocked internal hostname '%s'", hostname, extra={"event": "blocked_internal_url", "url": url})
            raise ValueError(f"Access to internal hostname '{hostname}' is blocked.")

        # Resolve hostname to IP address
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for family, socktype, proto, canonname, sockaddr in addr_info:
                ip_str = sockaddr[0]
                ip_obj = ipaddress.ip_address(ip_str)

                for blocked_net in BLOCKED_IP_NETWORKS:
                    if ip_obj in blocked_net:
                        jarvis_logger.warning("SSRF blocked private IP '%s' for host '%s'", ip_str, hostname, extra={"event": "blocked_internal_url", "url": url})
                        raise ValueError(f"Access to private/internal IP address '{ip_str}' is blocked for security reasons.")
        except socket.gaierror as exc:
            raise ValueError(f"Could not resolve hostname '{hostname}': {str(exc)}")

        return url
