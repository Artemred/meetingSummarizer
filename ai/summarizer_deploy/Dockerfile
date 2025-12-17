FROM ollama/ollama:latest

ARG GGUF_FILE=qwen2.5-7b-finetuned.gguf
ARG MODEL_NAME=model7

COPY ./${GGUF_FILE} /root/qwen2.5-7b-finetuned.gguf

COPY ./Modelfile7 /root/Modelfile

RUN nohup bash -c "ollama serve &" && sleep 5 && \
    ollama create ${MODEL_NAME} -f /root/Modelfile && \
    rm /root/qwen2.5-7b-finetuned.gguf && \
    rm /root/Modelfile

EXPOSE 11434

ENTRYPOINT ["/bin/ollama"]
CMD ["serve"]