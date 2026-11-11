FROM golang:1.24-alpine AS build

RUN CGO_ENABLED=0 go install -p 2 github.com/minio/minio@RELEASE.2025-10-15T17-29-55Z

FROM alpine:3.22
LABEL org.opencontainers.image.source="https://github.com/minio/minio"
LABEL org.opencontainers.image.version="RELEASE.2025-10-15T17-29-55Z"
RUN addgroup -S minio && adduser -S -G minio minio && mkdir /data && chown minio:minio /data
COPY --from=build /go/bin/minio /usr/local/bin/minio
USER minio
ENTRYPOINT ["/usr/local/bin/minio"]
CMD ["server", "/data"]
