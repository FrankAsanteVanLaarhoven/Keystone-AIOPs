# One-command reproduction image. Builds a clean, pinned environment and runs the
# documented evidence protocol (tests + benchmark scoreboard + evidence pack),
# exiting nonzero on any failure. For external reviewers with only Docker installed:
#
#   docker build -f deploy/repro.Dockerfile \
#     --build-arg VERDICTPLANE_REPRO_COMMIT=$(git rev-parse HEAD) \
#     -t verdictplane-repro .
#   docker run --rm verdictplane-repro
#
# Or simply: `make repro`.
FROM python:3.13-slim

ARG VERDICTPLANE_REPRO_COMMIT=local
ENV VERDICTPLANE_REPRO_COMMIT=${VERDICTPLANE_REPRO_COMMIT} \
    PYTHONUNBUFFERED=1 \
    VERDICTPLANE_ADVISORY=off

WORKDIR /verdictplane

# Everything the reproduction protocol touches (no .git, no network needed).
COPY pyproject.toml README.md Makefile ./
COPY src ./src
COPY tests ./tests
COPY bench ./bench
COPY scripts ./scripts
COPY policies ./policies
COPY workloads ./workloads
COPY benchmarks ./benchmarks
COPY docs ./docs

RUN pip install --no-cache-dir ".[dev]"

# Run the protocol as a non-root user against a writable copy.
RUN useradd --create-home reviewer && chown -R reviewer:reviewer /verdictplane
USER reviewer

ENTRYPOINT ["sh", "scripts/repro.sh"]
