# Multi-stage build for portal-ui (Vite + React)

# Build stage
FROM node:20-alpine AS build
WORKDIR /app

# Install pnpm via corepack and copy lockfiles for deterministic installs
COPY package.json pnpm-lock.yaml* ./
RUN corepack enable && pnpm install --frozen-lockfile

# Copy rest of the source and build
COPY . .
RUN pnpm build

# Production stage - serve with nginx
FROM nginx:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html

# Optional: add basic nginx config to support SPA routing
# (nginx default is fine for simple apps; customize if needed)
EXPOSE 5173
CMD ["nginx", "-g", "daemon off;"]
