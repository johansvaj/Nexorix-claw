import asyncio
import json
from typing import Dict, List

class MCPClientV2:
    def __init__(self):
        self.server_process = None
        self.tools = []
    async def start_server(self, server_cmd: List[str]):
        self.server_process = await asyncio.create_subprocess_exec(
            *server_cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await self._send_request("initialize", {"protocolVersion": "0.1.0"})
        res = await self._send_request("tools/list", {})
        self.tools = res.get("tools", [])
        return True
    async def _send_request(self, method: str, params: Dict):
        req = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
        self.server_process.stdin.write((json.dumps(req) + "\n").encode())
        await self.server_process.stdin.drain()
        line = await self.server_process.stdout.readline()
        return json.loads(line).get("result", {})
    async def call_tool(self, name: str, args: Dict) -> str:
        res = await self._send_request("tools/call", {"name": name, "arguments": args})
        if "content" in res:
            return res["content"][0].get("text", "")
        return str(res)
    async def close(self):
        if self.server_process:
            self.server_process.terminate()
            await self.server_process.wait()
