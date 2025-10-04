#!/usr/bin/env bash
set -o errexit -o nounset -o pipefail

# Variables (can be overridden via environment)
db_user="${db_user:-ufrecs}"
db_pass="${db_pass:-ufrecs}"
db_name="${db_name:-ufrecs}"

# Defaults for config templates (override with env or flags)
nginx_conf_src="${nginx_conf_src:-ufrecs/confs/ufrecs-nginx.conf}"
supervisor_conf_src="${supervisor_conf_src:-confs/ufrecs-supervisor.conf}"

# Step toggles
SKIP_DEPS=0
SKIP_DB=0
SKIP_UV=0
SKIP_PROJECT=0
SKIP_NGINX=0
SKIP_SUPERVISOR=0
SKIP_SERVICES=0
SKIP_PERMS=0
FORCE_CONFIGS=0

usage() {
    cat <<EOF
Usage: $0 [options]

Options:
  --db-name NAME             Database name (default: ${db_name})
  --db-user USER             Database user (default: ${db_user})
  --db-pass PASS             Database password (default: ${db_pass})
  --nginx-conf-src PATH      Source nginx conf template (default: ${nginx_conf_src})
  --supervisor-conf-src PATH Source supervisor conf template (default: ${supervisor_conf_src})

  --skip-deps                Skip apt install step
  --skip-db                  Skip database configuration
  --skip-uv                  Skip uv installation check
  --skip-project             Skip venv creation and uv sync
  --skip-nginx               Skip nginx configuration
  --skip-supervisor          Skip supervisor configuration
  --skip-services            Skip service restarts/reloads
  --skip-perms               Skip home permission adjustments
  --force-configs            Overwrite existing nginx/supervisor configs

  -h, --help                 Show this help
EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --db-name)
                db_name="$2"; shift 2 ;;
            --db-user)
                db_user="$2"; shift 2 ;;
            --db-pass)
                db_pass="$2"; shift 2 ;;
            --nginx-conf-src)
                nginx_conf_src="$2"; shift 2 ;;
            --supervisor-conf-src)
                supervisor_conf_src="$2"; shift 2 ;;
            --skip-deps)
                SKIP_DEPS=1; shift ;;
            --skip-db)
                SKIP_DB=1; shift ;;
            --skip-uv)
                SKIP_UV=1; shift ;;
            --skip-project)
                SKIP_PROJECT=1; shift ;;
            --skip-nginx)
                SKIP_NGINX=1; shift ;;
            --skip-supervisor)
                SKIP_SUPERVISOR=1; shift ;;
            --skip-services)
                SKIP_SERVICES=1; shift ;;
            --skip-perms)
                SKIP_PERMS=1; shift ;;
            --force-configs)
                FORCE_CONFIGS=1; shift ;;
            -h|--help)
                usage; exit 0 ;;
            *)
                echo "Unknown argument: $1" >&2
                usage; exit 1 ;;
        esac
    done
}

install_dependencies() {
    # Install required system packages
    sudo apt update
    sudo apt install nginx supervisor postgresql git curl -y
}

configure_database() {
    # Configure PostgreSQL database and role (idempotent)
    # Create user if missing
    if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='${db_user}'" | grep -q 1; then
        sudo -u postgres psql -c "CREATE USER \"${db_user}\" WITH PASSWORD '${db_pass}';"
    fi
    # Create database if missing
    if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='${db_name}'" | grep -q 1; then
        sudo -u postgres psql -c "CREATE DATABASE \"${db_name}\" OWNER \"${db_user}\";"
    fi
    # Grants and role settings (safe to repeat)
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE \"${db_name}\" TO \"${db_user}\";"
    sudo -u postgres psql -d "${db_name}" -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO \"${db_user}\";"
    sudo -u postgres psql -c "ALTER ROLE \"${db_user}\" SET client_encoding TO 'utf8';"
    sudo -u postgres psql -c "ALTER ROLE \"${db_user}\" SET default_transaction_isolation TO 'read committed';"
    sudo -u postgres psql -c "ALTER ROLE \"${db_user}\" SET timezone TO 'UTC';"
    sudo -u postgres psql -c "ALTER USER \"${db_user}\" CREATEDB;"
}

ensure_uv() {
    # Install UV if missing and ensure PATH is set
    if [ ! -f "$HOME/.local/bin/uv" ]; then
        # Install UV
        curl -LsSf https://astral.sh/uv/install.sh | sh

        # Update PATH to make uv available right now
        if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
            source ~/.bashrc
        fi

        # Add ~/.local/bin to PATH if it exists and isn't already there
        if [[ -d "$HOME/.local/bin" ]] && [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            export PATH="$HOME/.local/bin:$PATH"
        fi
    fi
}

configure_project() {
    # Create and activate virtual environment; sync dependencies
    if [ ! -d ~/ufrecs/venv ]; then
        uv venv --python 3.10 ufrecs/venv --prompt=ufrecs
    fi

    source ufrecs/venv/bin/activate
    cd ufrecs && uv sync --active && cd ..
}

configure_nginx() {
    # Copy Nginx config if not present or force overwrite
    if [ ! -f /etc/nginx/conf.d/ufrecs.conf ] || [ "$FORCE_CONFIGS" -eq 1 ]; then
        if [ ! -f "$nginx_conf_src" ]; then
            echo "Warning: nginx conf template not found at $nginx_conf_src; skipping nginx config." >&2
            return 0
        fi
        sudo sed "s/jefcolbi/$USER/g" "$nginx_conf_src" | sudo tee /etc/nginx/conf.d/ufrecs.conf > /dev/null
        sudo chown root:root /etc/nginx/conf.d/ufrecs.conf
        sudo chmod 644 /etc/nginx/conf.d/ufrecs.conf
    fi
}

configure_supervisor() {
    # Copy Supervisor config if not present or force overwrite
    if [ ! -f /etc/supervisor/conf.d/ufrecs.conf ] || [ "$FORCE_CONFIGS" -eq 1 ]; then
        if [ ! -f "$supervisor_conf_src" ]; then
            echo "Warning: supervisor conf template not found at $supervisor_conf_src; skipping supervisor config." >&2
            return 0
        fi
        sudo sed "s/jefcolbi/$USER/g" "$supervisor_conf_src" | sudo tee /etc/supervisor/conf.d/ufrecs.conf > /dev/null
        sudo chown root:root /etc/supervisor/conf.d/ufrecs.conf
        sudo chmod 644 /etc/supervisor/conf.d/ufrecs.conf
    fi
}

apply_service_changes() {
    # Apply service changes
    sudo systemctl restart nginx
    sudo supervisorctl reread
    sudo supervisorctl update
    sudo supervisorctl restart ufrecs-backend ufrecs-worker
}

fix_home_permissions() {
    # Various commands to serve web content from user home
    # You can add selinux commands here
    chmod o+rx "/home/$USER/"
}

main() {
    parse_args "$@"

    [ "$SKIP_DEPS" -eq 1 ] || install_dependencies
    [ "$SKIP_DB" -eq 1 ] || configure_database
    [ "$SKIP_UV" -eq 1 ] || ensure_uv
    [ "$SKIP_PROJECT" -eq 1 ] || configure_project
    [ "$SKIP_NGINX" -eq 1 ] || configure_nginx
    [ "$SKIP_SUPERVISOR" -eq 1 ] || configure_supervisor
    [ "$SKIP_SERVICES" -eq 1 ] || apply_service_changes
    [ "$SKIP_PERMS" -eq 1 ] || fix_home_permissions
}

main "$@"
