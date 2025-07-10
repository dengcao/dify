import json
from urllib.parse import urljoin, urlparse
from queue import Queue, Empty
from threading import Event,Thread

import httpx
from httpx_sse import connect_sse

class MCPClient:
    def __init__(self, sse_url, headers={}, timeout=5, sse_read_timeout=300):
        self.sse_url = sse_url
        self.timeout = timeout
        parsed_url = urlparse(sse_url)
        self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        self.message_endpoint = None
        self.session = httpx.Client(headers=headers, timeout=httpx.Timeout(timeout, read=sse_read_timeout))
        self._request_id = 0

        self.message_queue = Queue()
        self.response_ready = Event()
        self.should_stop = Event()
        self._listen_thread = None
        self._connected = Event()
        self.connect()

    def _listen_messages(self) -> None:
        with connect_sse(
            self.session, 
            "GET", 
            self.sse_url
        ) as event_source:
            event_source.response.raise_for_status()
        
            for event in event_source.iter_sse():
                if self.should_stop.is_set():
                    break
                if event.event == 'endpoint':
                    self.message_endpoint = event.data
                    self._connected.set()
                elif event.event == "message":
                    message = json.loads(event.data)
                    self.message_queue.put(message)
                    self.response_ready.set()

    def send_message(self, data: dict):
        if not self.message_endpoint:
            raise RuntimeError("please call connect() first")

        response = self.session.post(
            urljoin(self.base_url, self.message_endpoint),
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()

        if "id" in data:
            message_id = data["id"]
            while True:
                self.response_ready.wait()
                self.response_ready.clear()
                
                try:
                    while True:
                        message = self.message_queue.get_nowait()
                        if "id" in message and message["id"] == message_id:
                            self._request_id += 1
                            return message
                        self.message_queue.put(message)
                except Empty:
                    pass

        return {}

    def connect(self) -> None:
        self._listen_thread = Thread(target=self._listen_messages, daemon=True)
        self._listen_thread.start()
        
        if not self._connected.wait(timeout=self.timeout):
            raise TimeoutError("conection timeout!!")

    def close(self) -> None:
        self.should_stop.is_set()
        self.session.close()
        if self._listen_thread and self._listen_thread.is_alive():
            self._listen_thread.join(timeout=1)

    def initialize(self):

        init_data = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "mcp",
                    "version": "0.1.0"
                }
            }
        }

        init_result = self.send_message(init_data)

        notify_data = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        self.send_message(notify_data)

        return init_data

    def list_tools(self):
        tools_data = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": "tools/list",
            "params": {}
        }
        return self.send_message(tools_data).get("result",{}).get("tools",[])

    def call_tool(self, tool_name: str, tool_args: dict):
        call_data = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": tool_args
            }
        }
        return self.send_message(call_data).get("result", {}).get("content", [])


def main():
    try:
        client = MCPClient()
        print(f"connected to {client.sse_url}")

        init_result = client.initialize()
        print("init:", init_result)

        tools = client.list_tools()
        print("list tools:", tools)

        result = client.call_tool("get_alerts", {"state": "CA"})
        print("call tool:", result)

    finally:
        client.close()

if __name__ == "__main__":
    main()