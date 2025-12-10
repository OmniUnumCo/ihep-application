# Dockerfile for IAM Service
FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY iam_service/go.mod iam_service/go.sum ./
RUN go mod download

COPY iam_service/ .
RUN CGO_ENABLED=0 GOOS=linux go build -o iam-service .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/iam-service .
CMD ["./iam-service"]
