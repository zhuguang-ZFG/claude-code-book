#!/usr/bin/env python3
"""Tool calling and a minimal MCP-shaped JSON-RPC exchange. Stdlib only.

The model is a scripted list of calls, not a real model. The code shows the
contract a runtime enforces: schema validation, a permission-free toy executor,
error results, and the initialize / tools.list / tools.call messages MCP uses.
"""
from __future__ import annotations

import json
import re

TOOLS = {
    "get_refund_status": {
        "description": "查询订单的退款状态",
        "inputSchema": {
            "type": "object",
            "required": ["order_id"],
            "properties": {
                "order_id": {"type": "string", "pattern": r"^ORD-\d{4}$"},
            },
            "additionalProperties": False,
        },
    },
    "create_ticket": {
        "description": "为订单创建人工工单",
        "inputSchema": {
            "type": "object",
            "required": ["order_id", "reason"],
            "properties": {
                "order_id": {"type": "string", "pattern": r"^ORD-\d{4}$"},
                "reason": {"type": "string", "enum": ["延迟", "金额", "其他"]},
            },
            "additionalProperties": False,
        },
    },
}

ORDERS = {
    "ORD-1001": "退款处理中，预计 1–3 个工作日到账",
    "ORD-1002": "已退款，原路退回",
}
SCRIPTED_CALLS = [
    {"name": "get_refund_status", "arguments": {"order_id": 1001}},
    {"name": "get_refund_status", "arguments": {"order_id": "ORD-1001"}},
]


def validate(name: str, arguments: dict) -> list[str]:
    tool = TOOLS.get(name)
    if tool is None:
        return [f"unknown tool: {name}"]
    schema = tool["inputSchema"]
    errors = []
    for field in schema.get("required", []):
        if field not in arguments:
            errors.append(f"missing required field: {field}")
    for field, value in arguments.items():
        spec = schema["properties"].get(field)
        if spec is None:
            errors.append(f"unexpected field: {field}")
            continue
        if spec["type"] == "string" and not isinstance(value, str):
            errors.append(f"{field} must be a string")
        elif spec["type"] == "string" and "pattern" in spec:
            if not re.fullmatch(spec["pattern"], value):
                errors.append(f"{field} does not match {spec['pattern']}")
        if "enum" in spec and value not in spec["enum"]:
            errors.append(f"{field} must be one of {spec['enum']}")
    return errors


def execute(name: str, arguments: dict) -> dict:
    if name == "get_refund_status":
        order = arguments["order_id"]
        if order not in ORDERS:
            return {"isError": True, "content": f"order not found: {order}"}
        return {"isError": False, "content": ORDERS[order]}
    if name == "create_ticket":
        return {"isError": False,
                "content": f"ticket created for {arguments['order_id']} "
                           f"({arguments['reason']})"}
    return {"isError": True, "content": f"unknown tool: {name}"}


def call_tool(name: str, arguments: dict) -> dict:
    errors = validate(name, arguments)
    if errors:
        return {"isError": True, "content": "validation failed: " +
                "; ".join(errors)}
    return execute(name, arguments)


def mcp_messages() -> list[dict]:
    return [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2026-07-28", "capabilities": {},
                    "clientInfo": {"name": "toy-agent", "version": "0.1"}}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "get_refund_status",
                    "arguments": {"order_id": "ORD-1001"}}},
    ]


def main() -> int:
    print("tool schemas")
    for name, tool in TOOLS.items():
        raw = json.dumps(tool, ensure_ascii=False, separators=(",", ":"))
        print(f"  {name}: {len(raw)} chars, "
              f"{len(tool['inputSchema'].get('required', []))} required fields")
    print()

    print("scripted tool loop")
    for attempt, call in enumerate(SCRIPTED_CALLS, 1):
        result = call_tool(call["name"], call["arguments"])
        print(f"  attempt {attempt}: {json.dumps(call, ensure_ascii=False)}")
        print(f"    -> {json.dumps(result, ensure_ascii=False)}")
    print()

    print("unknown tool")
    print("  " + json.dumps(call_tool("delete_order", {"order_id": "ORD-1001"}),
                            ensure_ascii=False))
    print()

    print("MCP-shaped JSON-RPC")
    for message in mcp_messages():
        print("  " + json.dumps(message, ensure_ascii=False))
    call = mcp_messages()[-1]["params"]
    result = call_tool(call["name"], call["arguments"])
    response = {"jsonrpc": "2.0", "id": 3,
                "result": {"content": [{"type": "text",
                                        "text": result["content"]}],
                           "isError": result["isError"]}}
    print("  " + json.dumps(response, ensure_ascii=False))
    print()
    print("note: this toy has no permissions, transport, timeouts or idempotency; "
          "a real runtime must add them before exposing tools to a model")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
