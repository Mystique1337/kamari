# Web app (Vite PWA) for Railway. Multi-stage: build, then serve as static with SPA fallback.
# Set VITE_* as Railway build variables so they are baked into the bundle.
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG VITE_KAMARI_API_URL
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY
ARG VITE_USE_MOCK=0
ENV VITE_KAMARI_API_URL=$VITE_KAMARI_API_URL \
    VITE_SUPABASE_URL=$VITE_SUPABASE_URL \
    VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY \
    VITE_USE_MOCK=$VITE_USE_MOCK
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Railway provides $PORT; rewrite nginx to listen on it at start.
CMD ["sh", "-c", "sed -i \"s/listen 80;/listen ${PORT:-80};/\" /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
