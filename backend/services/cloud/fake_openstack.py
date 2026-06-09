import ipaddress
import random
import uuid

from services.cloud.provider import CloudProvider, CloudServer


class FakeOpenStackProvider(CloudProvider):
    """In-memory provider that mirrors the OpenStack-shaped contract."""

    _servers: dict[str, CloudServer] = {}

    def create_server(self, *, name: str, vcpu: int, ram_mb: int, disk_gb: int) -> CloudServer:
        server = CloudServer(server_id=str(uuid.uuid4()), status="BUILD")
        self._servers[server.server_id] = server
        return server

    def get_server(self, server_id: str) -> CloudServer:
        server = self._servers.get(server_id)
        if server and server.status == "ACTIVE" and server.ip_address:
            return server
        active = CloudServer(server_id=server_id, status="ACTIVE", ip_address=self._private_ip())
        self._servers[server_id] = active
        return active

    def stop_server(self, server_id: str) -> CloudServer:
        current = self.get_server(server_id)
        stopped = CloudServer(server_id=server_id, status="SHUTOFF", ip_address=current.ip_address)
        self._servers[server_id] = stopped
        return stopped

    def start_server(self, server_id: str) -> CloudServer:
        current = self.get_server(server_id)
        active = CloudServer(server_id=server_id, status="ACTIVE", ip_address=current.ip_address or self._private_ip())
        self._servers[server_id] = active
        return active

    def delete_server(self, server_id: str) -> CloudServer:
        current = self.get_server(server_id)
        deleted = CloudServer(server_id=server_id, status="DELETED", ip_address=current.ip_address)
        self._servers[server_id] = deleted
        return deleted

    @staticmethod
    def _private_ip() -> str:
        base = ipaddress.ip_address("10.42.0.1")
        return str(base + random.randint(10, 5000))
