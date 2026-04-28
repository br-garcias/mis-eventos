FROM node:22-alpine AS base


FROM base AS deps

RUN apk add --no-cache libc6-compat

WORKDIR /app

COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./
RUN \
    if [ -f yarn.lock ]; then yarn --frozen-lockfile; \
    elif [ -f package-lock.json ]; then npm ci; \
    elif [ -f pnpm-lock.yaml ]; then yarn global add pnpm && pnpm i; \
    else echo "Lockfile not found." && exit 1; \
    fi


FROM base AS builder

ARG VITE_API_URL

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN VITE_API_URL=$VITE_API_URL
RUN yarn build


FROM nginx:stable-alpine

RUN apk --no-cache add curl

COPY --from=builder /app/dist /usr/share/nginx/app
COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN chown -R nginx:nginx /usr/share/nginx/app

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
