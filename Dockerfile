# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM python:3.12-slim

# git required for uvx to fetch fivetran-mcp from GitHub at build time
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv==0.8.13

WORKDIR /code

COPY ./pyproject.toml ./README.md ./uv.lock* ./

COPY ./app ./app
COPY ./knowledge ./knowledge

# Frontend (pre-built)
COPY ./frontend/dist ./frontend/dist

RUN uv sync --frozen

# Pre-install Fivetran MCP server so Cloud Run does not fetch from Git at runtime
ENV FIVETRAN_MCP_COMMAND=uvx
ENV FIVETRAN_MCP_ARGS=--from,git+https://github.com/fivetran/fivetran-mcp,fivetran-mcp
RUN uvx --from git+https://github.com/fivetran/fivetran-mcp fivetran-mcp --help >/dev/null 2>&1 || true

ARG COMMIT_SHA=""
ENV COMMIT_SHA=${COMMIT_SHA}

ARG AGENT_VERSION=0.0.0
ENV AGENT_VERSION=${AGENT_VERSION}

EXPOSE 8080

CMD ["uv", "run", "uvicorn", "app.fast_api_app:app", "--host", "0.0.0.0", "--port", "8080"]