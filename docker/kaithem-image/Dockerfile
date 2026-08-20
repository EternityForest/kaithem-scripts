FROM debian:trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app



RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt update && apt install -y make sudo git



WORKDIR /app/debian

# RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
#     --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
#     make root-install-system-dependencies


# Mount host-cached directories into the container during the build phase
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt install -y python3 mpv lm-sensors python3-gst-1.0  gstreamer1.0-plugins-good  gstreamer1.0-plugins-bad gstreamer1.0-tools swh-plugins  tap-plugins  caps   gstreamer1.0-plugins-ugly libfluidsynth3 gstreamer1.0-pocketsphinx x42-plugins gstreamer1.0-opencv  gstreamer1.0-vaapi gstreamer1.0-pipewire build-essential libasound2-dev libjack-jackd2-dev pipewire-jack

# Copy dependency definition files first for efficient layering

COPY . .

RUN mkdir -p /app/debian/gits

RUN --mount=type=cache,target=/app/debian/gits,sharing=locked \
    [ -d /app/debian/gits/KaithemAutomation ] || git clone --depth 1 https://github.com/EternityForest/KaithemAutomation /app/debian/gits/KaithemAutomation

RUN --mount=type=cache,target=/app/debian/gits,sharing=locked \
    cd /app/debian/gits/KaithemAutomation && git pull origin master


ENV UV_TOOL_DIR=/opt/uv-tools
ENV UV_TOOL_BIN_DIR=/usr/local/bin

RUN --mount=type=cache,target=/app/debian/gits,sharing=locked \
    UV_LINK_MODE=copy uv tool install --verbose /app/debian/gits/KaithemAutomation


# UV_LINK_MODE=copy ensures packages are physically copied into the 
# image rather than hardlinked from the temporary cache mount.
# RUN --mount=type=cache,target=/root/.cache/uv \
#     UV_LINK_MODE=copy make user-install-kaithem

ENTRYPOINT ["pw-jack", "kaithem"]