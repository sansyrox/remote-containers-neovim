FROM mcr.microsoft.com/devcontainers/python:0-3.11-bullseye
COPY ./config/nvim /root/.config/nvim
RUN apt-get update && apt-get install -y curl git

                # Install dependencies for building Neovim
RUN apt-get update && apt-get install -y     ninja-build gettext libtool libtool-bin autoconf automake cmake g++ pkg-config unzip

# Clone the Neovim repository
RUN git clone https://github.com/neovim/neovim.git /root/neovim

# Build Neovim
RUN cd /root/neovim && make CMAKE_BUILD_TYPE=Release && make install
                

# Install Plug for Neovim
RUN curl -fLo /root/.config/nvim/autoload/plug.vim --create-dirs     https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim

# Copy the Neovim configuration files
COPY ./config/nvim /root/.config/nvim


# Install plugins with PlugInstall
RUN nvim --headless +PlugInstall +qall

# Set the default command to run neovim
CMD ["nvim"]
                