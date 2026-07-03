# Keystone sidecar image: the governance library + reviewer CLI, nothing else.
# Runtime needs no network at all — compose runs it with network_mode: "none".
FROM python:3.13-slim

WORKDIR /keystone
COPY pyproject.toml README.md ./
COPY src ./src
COPY policies ./policies
COPY workloads ./workloads
COPY deploy/demo_agent.py ./deploy/demo_agent.py

RUN pip install --no-cache-dir . \
    && useradd --create-home keystone \
    && mkdir -p /data && chown keystone:keystone /data
USER keystone

# Shared volume: ledger + gate queue. The reviewer container resolves what the
# agent container is blocked on, through the filesystem alone.
ENV KEYSTONE_LEDGER=/data/ledger.jsonl \
    KEYSTONE_GATE=/data/gate \
    PYTHONUNBUFFERED=1

ENTRYPOINT ["keystone"]
CMD ["pending"]
