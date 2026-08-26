FROM python:3.12-slim

# Librairies systeme exigees par OpenCASCADE (OCP), opencv-headless et le rendu
# de texte build123d (fontconfig + une police reelle pour Text()).
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglu1-mesa \
        libxrender1 \
        libxext6 \
        libxi6 \
        libsm6 \
        libgomp1 \
        fontconfig \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv

# 1) dependances d'abord (cache Docker : ne se reinstalle que si requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) le code applicatif
COPY app ./app

# Render fournit $PORT ; en local on retombe sur 8009.
ENV PORT=8009
EXPOSE 8009

CMD ["sh", "-c", "uvicorn app.server:app --host 0.0.0.0 --port ${PORT:-8009}"]
