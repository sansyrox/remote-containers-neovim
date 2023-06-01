import os
import json
import subprocess
from pathlib import Path

def find_devcontainer_file(project_dir):
    for root, dirs, files in os.walk(project_dir):
        if 'devcontainer.json' in files:
            return os.path.join(root, 'devcontainer.json')
    return None

def parse_devcontainer_file(filepath):
    with open(filepath) as f:
        data = json.load(f)
    return data

def create_neovim_dockerfile(data, dockerfile_path):
    path = Path("~/.config/nvim").expanduser()
    # copy the neovim config to the local folder
    os.system(f"rsync -v {path} config --exclude 'plugged' --exclude 'autoload'")
    
    with open(dockerfile_path, 'w') as f:
        f.write("FROM " + data['image'] + "\n")
        f.write(f"COPY ./config/nvim /root/.config/nvim\n")
        f.write("RUN apt-get update && apt-get install -y curl git\n")
        f.write("""
                # Install dependencies for building Neovim
RUN apt-get update && apt-get install -y \
    ninja-build gettext libtool libtool-bin autoconf automake cmake g++ pkg-config unzip

# Clone the Neovim repository
RUN git clone https://github.com/neovim/neovim.git /root/neovim

# Build Neovim
RUN cd /root/neovim && make CMAKE_BUILD_TYPE=Release && make install
                

# Install Plug for Neovim
RUN curl -fLo /root/.config/nvim/autoload/plug.vim --create-dirs \
    https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim

# Copy the Neovim configuration files
COPY ./config/nvim /root/.config/nvim


# Install plugins with PlugInstall
RUN nvim --headless +PlugInstall +qall

# Set the default command to run neovim
CMD ["nvim"]
                """)

def build_and_run_docker_image(dockerfile_path):
    build_command = "docker build -t neovim_container -f " + dockerfile_path + " ."
    run_command = "docker run -it neovim_container"

    subprocess.run(build_command, shell=True, check=True)
    subprocess.run(run_command, shell=True, check=True)

def main():
    project_dir = "."  # Adjust to your need
    dockerfile_path = "./Dockerfile"
    devcontainer_filepath = find_devcontainer_file(project_dir)

    if devcontainer_filepath:
        data = parse_devcontainer_file(devcontainer_filepath)
        create_neovim_dockerfile(data, dockerfile_path)
        build_and_run_docker_image(dockerfile_path)
    else:
        print("No devcontainer.json file found in the project directory.")

if __name__ == "__main__":
    main()


