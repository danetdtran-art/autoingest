FROM golang:1.26-alpine AS builder
RUN apk --no-cache add gcc musl-dev
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=1 GOOS=linux go build -o autoingest ./cmd/server/

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/autoingest .
RUN chmod +x autoingest
RUN mkdir -p /data/uploads /data/templates /data/static

EXPOSE 8080
CMD ["./autoingest"]
