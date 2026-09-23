# Production image for the DevTrack frontend: a Vite/React SPA built to
# static files and served by nginx (no Node/dev server in the final image).
#
# VITE_API_BASE_URL is baked into the JS bundle at BUILD time, not read at
# container runtime — Vite env vars are compiled into the client bundle that
# runs in the end user's browser, so there is no "runtime env" to change
# after the image is built. Pass it as a build arg:
#
#   docker build --build-arg VITE_API_BASE_URL=https://api.example.com .
#
# It must be a URL reachable from the *browser*, never a Docker-internal
# service name like http://backend:8000 — see README for details.

# --- Build stage ---
FROM node:22-alpine AS build
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# --- Production stage ---
FROM nginx:1.27-alpine AS production

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
