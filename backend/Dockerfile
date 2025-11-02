FROM golang:1.22-alpine
WORKDIR /app
COPY . .
RUN go mod init guidora-backend && go get github.com/gin-gonic/gin && go get github.com/google/generative-ai-go/genai
RUN go build -o backend main.go
EXPOSE 8080
CMD ["./backend"]
