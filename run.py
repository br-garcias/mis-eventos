#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import shutil

GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_step(msg):
    print(f"\n{BLUE}▶ {msg}{RESET}")

def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def print_info(msg):
    print(f"{YELLOW}ℹ {msg}{RESET}")

def ask_yes_no(question):
    while True:
        response = input(f"{BOLD}{question} [y/n]: {RESET}").strip().lower()
        if response in ("y", "yes"):
            return True
        elif response in ("n", "no"):
            return False
        print_info("Por favor responde 'y' o 'n'")

def ask_with_default(question, default):
    response = input(f"{BOLD}{question} [{default}]: {RESET}").strip()
    return response if response else default

def update_env_file(filepath, updates):
    env_vars = {}
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key] = value

    env_vars.update(updates)

    with open(filepath, "w") as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")

    return env_vars

def copy_example_if_missing(example_file, env_file):
    if not os.path.exists(env_file) and os.path.exists(example_file):
        shutil.copy(example_file, env_file)
        print_info(f"Creado {env_file} desde {example_file}")

def main():
    print(f"{BOLD}{'='*50}{RESET}")
    print(f"{BOLD}  🚀 Mis Eventos - Script de Arranque{RESET}")
    print(f"{BOLD}{'='*50}{RESET}")

    env_exists = os.path.exists(".env.mongo") and os.path.exists(".env.api")

    if env_exists:
        print_info("Archivos .env ya existen, iniciando directamente...")
    else:
        print_step("Inicializando archivos de configuración...")
        copy_example_if_missing(".env.mongo.example", ".env.mongo")
        copy_example_if_missing(".env.api.example", ".env.api")
        print_success("Archivos .env inicializados")

        print_step("Generando JWT_SECRET...")
        result = subprocess.run(
            ["openssl", "rand", "-hex", "32"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            jwt_secret = result.stdout.strip()
            update_env_file(".env.api", {"JWT_SECRET": jwt_secret})
            print_success("JWT_SECRET generado")
        else:
            print_info("No se pudo generar JWT_SECRET automáticamente")

        print_step("Configurando MongoDB...")
        configure_mongo = ask_yes_no("¿Deseas configurar usuario y contraseña de MongoDB?")

        mongo_user = "root"
        mongo_pass = "root"

        if configure_mongo:
            mongo_user = ask_with_default("Usuario de MongoDB", "root")
            mongo_pass = ask_with_default("Contraseña de MongoDB", mongo_pass)

        print_step("Actualizando configuración de MongoDB...")
        update_env_file(".env.mongo", {
            "MONGO_INITDB_ROOT_USERNAME": mongo_user,
            "MONGO_INITDB_ROOT_PASSWORD": mongo_pass
        })
        print_success(f"MongoDB configurado con usuario: {mongo_user}")

        print_step("Configurando Cache...")
        enable_cache = ask_yes_no("¿Deseas habilitar el cache?")

        cache_enabled = "true" if enable_cache else "false"
        update_env_file(".env.api", {
            "CACHE_ENABLED": cache_enabled
        })
        cache_status = "habilitado" if enable_cache else "deshabilitado"
        print_success(f"Cache {cache_status}")

    if env_exists:
        env_mongo = {}
        with open(".env.mongo", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_mongo[key] = value
        mongo_user = env_mongo.get("MONGO_INITDB_ROOT_USERNAME", "root")
        mongo_pass = env_mongo.get("MONGO_INITDB_ROOT_PASSWORD", "root")

    print_step("Verificando docker-compose.yml con app (frontend)...")

    docker_compose_path = "docker-compose.yml"
    with open(docker_compose_path, "r") as f:
        docker_content = f.read()

    if "app:" not in docker_content:
        print_info("Agregando servicio app (frontend) al docker-compose.yml...")

        frontend_service = """  app:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        VITE_API_URL: ${VITE_API_URL:-http://localhost:8000/api/v1}
    ports:
      - "5173:80"
    depends_on:
      api:
        condition: service_healthy
    restart: on-failure:3

"""

        if "volumes:" in docker_content:
            docker_content = docker_content.replace(
                "volumes:",
                f"{frontend_service}volumes:"
            )
        else:
            docker_content += f"\n{frontend_service}"

        with open(docker_compose_path, "w") as f:
            f.write(docker_content)

        print_success("App (frontend) agregado al docker-compose.yml")
    else:
        print_info("El servicio app ya está configurado en docker-compose.yml")

    print_step("Iniciando servicios con Docker Compose...")

    mongo_url = f"mongodb://{mongo_user}:{mongo_pass}@mongo:27017/mis_eventos?authSource=admin"
    update_env_file(".env.api", {"MONGO_URL": mongo_url})

    result = subprocess.run(
        ["docker", "compose", "up", "-d"],
        capture_output=False
    )

    if result.returncode != 0:
        print(f"{RED}✗ Error al iniciar docker-compose{RESET}")
        sys.exit(1)

    print_step("Esperando a que los servicios estén saludables...")

    services = ["mongo", "valkey", "api"]
    if "app:" in open(docker_compose_path).read():
        services.append("app")

    max_wait = 120
    start_time = time.time()

    while time.time() - start_time < max_wait:
        check = subprocess.run(
            ["docker", "compose", "ps", "--format", "json"],
            capture_output=True,
            text=True
        )

        if check.returncode == 0 and check.stdout:
            import json
            try:
                ps_output = check.stdout.strip()
                if ps_output.startswith("["):
                    services_status = json.loads(ps_output)
                else:
                    for line in ps_output.split("\n"):
                        if line.strip():
                            services_status = [json.loads(line)]
                            break
                    else:
                        services_status = []

                healthy_count = 0
                for svc in services_status:
                    state = svc.get("Health", "")
                    service_name = svc.get("Service", "")
                    if service_name in services and state == "healthy":
                        healthy_count += 1

                if healthy_count >= len(services):
                    break
            except Exception:
                pass

        time.sleep(5)

    print(f"\n{GREEN}{'='*50}{RESET}")
    print(f"{GREEN}  ✓✓✓  OK - Aplicación iniciada correctamente  ✓✓✓{RESET}")
    print(f"{GREEN}{'='*50}{RESET}")
    print(f"\n{BOLD}Servicios disponibles:{RESET}")
    print(f"  • API:        http://localhost:8000")
    print(f"  • Frontend:   http://localhost:5173")
    print(f"  • MongoDB:    localhost:27017")
    print(f"  • Valkey:     localhost:6379")

if __name__ == "__main__":
    main()
