FROM ollama/ollama:latest

# Create a script that will pull the model on first run
RUN mkdir -p /app
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
