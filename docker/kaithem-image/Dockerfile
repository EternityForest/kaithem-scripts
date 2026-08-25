FROM debian:trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


# Apt update only if we really have to
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    bash -c '[ -z "$(find /var/cache/apt/pkgcache.bin -mmin -1440 2>/dev/null)" ] && apt-get update'

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get install -y \
    curl \
    build-essential \
    make sudo git unzip

RUN curl -fsSL https://fnm.vercel.app/install | bash

RUN /root/.local/share/fnm/fnm install --lts

# Install Rust non-interactively

RUN     --mount=type=cache,target=/root/.cargo \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Configure the environment path manually
ENV PATH="/root/.cargo/bin:${PATH}"

RUN --mount=type=cache,target=/root/.cargo \
    rustup target add wasm32-unknown-unknown

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app






WORKDIR /app/debian

# RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
#     --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
#     make root-install-system-dependencies


# Mount host-cached directories into the container during the build phase
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt install -y python3 mpv lm-sensors python3-gst-1.0  gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad gstreamer1.0-tools swh-plugins  tap-plugins \
    caps gstreamer1.0-plugins-ugly libfluidsynth3 gstreamer1.0-pocketsphinx \
    x42-plugins gstreamer1.0-opencv  gstreamer1.0-vaapi gstreamer1.0-pipewire \
    build-essential libasound2-dev libjack-jackd2-dev pipewire-jack gir1.2-gtk-3.0 \
    python3-venv gstreamer1.0-libav

# Copy dependency definition files first for efficient layering


COPY . .

RUN mkdir -p /app/debian/gits

RUN --mount=type=cache,target=/app/debian/gits,sharing=locked \
    [ -d /app/debian/gits/KaithemAutomation ] || git clone --depth 1 https://github.com/EternityForest/KaithemAutomation /app/debian/gits/KaithemAutomation


RUN echo 'eval "$(fnm env --use-on-cd)"' >> /root/.bashrc
ENV PATH="/root/.local/share/fnm/aliases/default/bin:$PATH"

RUN node -v && npx -v


RUN --mount=type=cache,target=/app/debian/gits,sharing=locked \
    cd /app/debian/gits/KaithemAutomation && git fetch origin master && git reset --hard origin/master



RUN --mount=type=cache,target=/app/debian/gits,sharing=locked \
    [ -d /app/debian/gits/Dashbeard ] || git clone --depth 1 https://github.com/EternityForest/Dashbeard /app/debian/gits/Dashbeard


RUN --mount=type=cache,target=/app/debian/gits,sharing=locked \
    cd /app/debian/gits/Dashbeard && git fetch origin main && git reset --hard origin/main


RUN --mount=type=cache,target=/root/.npm \
    --mount=type=cache,target=/app/debian/gits,sharing=locked \
    cd /app/debian/gits/KaithemAutomation && npm ci


RUN --mount=type=cache,target=/root/.npm \
    --mount=type=cache,target=/app/debian/gits,sharing=locked \
    cd /app/debian/gits/Dashbeard && npm ci


RUN --mount=type=cache,target=/app/debian/gits,sharing=locked \
    --mount=type=cache,target=/root/.npm \
    --mount=type=cache,target=/root/.cargo \
    --mount=type=cache,target=/app/target \
    --mount=type=cache,target=/root/.cache/uv \ 
    --mount=type=cache,target=/root/.local/share/uv \
    cd /app/debian/gits/KaithemAutomation && UV_LINK_MODE=copy uv sync && UV_LINK_MODE=copy make dev-build


ENV UV_TOOL_DIR=/opt/uv-tools
ENV UV_TOOL_BIN_DIR=/usr/local/bin

RUN --mount=type=cache,target=/app/debian/gits,sharing=locked \
    --mount=type=cache,target=/root/.local/share/uv \
    UV_LINK_MODE=copy uv tool install --verbose /app/debian/gits/KaithemAutomation

# The iceflow hack doesn't work with readonly images so
# Do it ahead of time.
RUN ln -s /usr/lib/python3/dist-packages/gi /opt/uv-tools/kaithem/lib/python3.13/site-packages/gi

# UV_LINK_MODE=copy ensures packages are physically copied into the 
# image rather than hardlinked from the temporary cache mount.
# RUN --mount=type=cache,target=/root/.cache/uv \
#     UV_LINK_MODE=copy make user-install-kaithem

ENTRYPOINT ["pw-jack", "kaithem"]