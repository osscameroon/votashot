install_uv() {
    # Check if UV is already installed
    if command -v uv >/dev/null 2>&1; then
        echo "UV is already installed"
        return 0
    fi

    echo "Installing UV..."

    # Detect OS type
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew >/dev/null 2>&1; then
            brew install uv
        else
            curl -LsSf https://astral.sh/uv/install.sh | sh
        fi
    elif [[ -f /etc/debian_version ]]; then
        # Debian-like (Ubuntu, Debian, etc.)
        if command -v apt-get >/dev/null 2>&1; then
            curl -LsSf https://astral.sh/uv/0.5.4/install.sh | sh
        else
            curl -LsSf https://astral.sh/uv/install.sh | sh
        fi
    elif [[ -f /etc/redhat-release ]] || [[ -f /etc/fedora-release ]] || [[ -f /etc/centos-release ]]; then
        # RPM-like (RHEL, CentOS, Fedora, etc.)
        curl -LsSf https://astral.sh/uv/install.sh | sh
    else
        # Generic Unix-like
        curl -LsSf https://astral.sh/uv/install.sh | sh
    fi

    # Update PATH to make uv available right now
    if [[ -d "$HOME/.local/bin" ]]; then
        if ! grep -q "export PATH=\"\$HOME/.local/bin:\$PATH\"" ~/.bashrc 2>/dev/null; then
            echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> ~/.bashrc
        fi

        # Add ~/.local/bin to PATH if it exists and isn't already there
        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            export PATH="$HOME/.local/bin:$PATH"
        fi
    fi

    # Verify installation
    if command -v uv >/dev/null 2>&1; then
        echo "UV installed successfully"
        uv --version
    else
        echo "UV installation failed"
        return 1
    fi
}

create_venv() {
    local parent_dir
    parent_dir="$(pwd)"
    local venv_path="$parent_dir/.venv"

    # Check if virtual environment already exists
    if [[ -d "$venv_path" ]]; then
        echo "Virtual environment already exists at: $venv_path"
        return 0
    fi

    echo "Creating virtual environment at: $venv_path"

    # Create virtual environment using uv with Python 3.10
    if command -v uv >/dev/null 2>&1; then
        # Use uv to create virtual environment with Python 3.10
        echo "Installing Python 3.10 and creating virtual environment with uv..."
        cd "$parent_dir" && uv venv .venv --python 3.10
    else
        # Fallback to python venv module
        if command -v python3.10 >/dev/null 2>&1; then
            cd "$parent_dir" && python3.10 -m venv .venv
        elif command -v python3 >/dev/null 2>&1; then
            cd "$parent_dir" && python3 -m venv .venv
        elif command -v python >/dev/null 2>&1; then
            cd "$parent_dir" && python -m venv .venv
        else
            echo "Error: Neither uv nor python found. Cannot create virtual environment."
            return 1
        fi
    fi

    # Verify virtual environment was created
    if [[ -d "$venv_path" ]]; then
        echo "Virtual environment created successfully at: $venv_path"

        # Show activation instructions
        echo ""
        echo "To activate the virtual environment, run:"
        echo "  source $venv_path/bin/activate"
        echo ""

        return 0
    else
        echo "Error: Failed to create virtual environment"
        return 1
    fi
}

install_uv

create_venv
