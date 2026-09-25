# Blue Hole – Unreal Remote Execution Patch

## Overview

This folder contains a patched version of Unreal / Send2UE's `remote_execution.py`.

The patch fixes an intermittent issue where Blue Hole could successfully send an asset to Unreal, Unreal would import the asset correctly, but Blender would still report:

```text
Remote party failed to send a valid response!
```

In some cases, the log also contained a JSON parsing error similar to:

```text
Unterminated string starting at: line 1 column 4043
```

The issue was caused by the TCP response handling in `remote_execution.py`.

---

## Original Problem

The original implementation received the Unreal command result using a single call:

```python
data = self._command_channel_socket.recv(4096)
```

It then immediately attempted to parse the returned data as a complete JSON message.

This is unsafe for TCP communication.

TCP is a byte stream and does not guarantee that one `recv()` call will contain one complete message. A JSON response may be split across multiple TCP packets.

For example:

```text
Unreal response:

[---------------- complete JSON response ----------------]

TCP receive:

[-------------- first 4096 bytes --------------]
                                                [remaining bytes]
```

The original code attempted to parse the first chunk immediately.

If the response was incomplete, JSON parsing failed even though Unreal had successfully executed the command.

This explains why the issue could appear intermittently depending on response size and timing.

---

## Changes

### 1. Accumulate TCP Response Data

The patched `_receive_message()` now accumulates data from multiple `recv(4096)` calls.

Instead of assuming the first chunk is complete, it continues receiving data until the accumulated response can be parsed as valid JSON.

Conceptually:

```text
Receive chunk
    ↓
Append to buffer
    ↓
Try parsing JSON
    ↓
Incomplete?
    ├── Yes → receive another chunk
    └── No  → validate and return response
```

This allows command responses larger than 4096 bytes, or responses split across multiple TCP packets, to be handled correctly.

---

### 2. Preserve Existing Remote Execution Validation

Once a complete JSON response has been received, the existing remote execution validation is still performed.

The patch verifies that:

- the response is valid JSON;
- the response passes the node receive filter;
- the response type matches the expected Unreal command result type.

Unexpected or invalid responses still raise a `RuntimeError`.

---

### 3. Add Command Socket Timeout

The original command socket was switched to fully blocking mode:

```python
self._command_channel_socket.setblocking(True)
```

The patched version instead uses:

```python
self._command_channel_socket.settimeout(30.0)
```

This prevents Blender from potentially waiting forever if Unreal begins sending a response but never completes it.

If no complete response is received within the timeout period, the connection raises a descriptive timeout error.

---

## What Was Not Changed

The patch intentionally keeps the rest of Epic's remote execution implementation unchanged.

In particular:

- UDP discovery behavior was not modified.
- The UDP `recv(4096)` call remains unchanged.
- Unreal node discovery remains unchanged.
- Command sending remains unchanged.
- The remote execution protocol remains unchanged.
- Blue Hole's export/import logic remains unchanged.

The UDP receive path does not have the same issue because UDP preserves datagram boundaries and the discovery messages are small.

---

## Why This Fix Is Needed

The failure occurred after Unreal had already executed the requested import.

The problem was therefore not the FBX export or Unreal import itself.

The failure occurred while Blender was receiving Unreal's command result.

The original implementation assumed:

```text
1 TCP recv() == 1 complete Unreal response
```

The patched implementation correctly handles:

```text
1 Unreal response == 1 or more TCP recv() calls
```

This should eliminate the intermittent `Remote party failed to send a valid response!` errors caused by fragmented or larger command responses.

---

## Patched File

Replace the existing:

```text
BlueHole/Lib/send2ue/dependencies/remote_execution.py
```

with the patched version of `remote_execution.py`.

Keep this README alongside the patched source as documentation for why the upstream file was modified.
