FROM node:18-slim AS builder
WORKDIR /app
COPY frontend/package*.json ./
COPY frontend/tsconfig*.json ./
COPY frontend/vite.config.ts ./
COPY frontend /app
RUN npm ci
RUN npm run build

FROM node:18-slim
WORKDIR /app
COPY --from=builder /app/dist /app/dist
RUN npm i -g serve
EXPOSE 5173
CMD ["serve", "-s", "dist", "-l", "5173"]
