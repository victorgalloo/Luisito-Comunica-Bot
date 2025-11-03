#!/bin/bash

# Script de deploy para Luisito Comunica Chatbot
# Uso: ./deploy.sh [opción]
# Opciones: local, railway, render, azure, vps

set -e  # Salir si hay error

COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_NC='\033[0m' # No Color

print_info() {
    echo -e "${COLOR_GREEN}ℹ️  $1${COLOR_NC}"
}

print_warning() {
    echo -e "${COLOR_YELLOW}⚠️  $1${COLOR_NC}"
}

print_error() {
    echo -e "${COLOR_RED}❌ $1${COLOR_NC}"
}

print_success() {
    echo -e "${COLOR_GREEN}✅ $1${COLOR_NC}"
}

# Verificar que .env existe
check_env() {
    if [ ! -f .env ]; then
        print_error ".env no encontrado. Crea uno basado en .env.example"
        exit 1
    fi
    print_success ".env encontrado"
}

# Verificar dependencias
check_dependencies() {
    print_info "Verificando dependencias..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado"
        exit 1
    fi
    print_success "Docker instalado"
    
    if ! command -v docker-compose &> /dev/null && ! command -v docker compose &> /dev/null; then
        print_error "Docker Compose no está instalado"
        exit 1
    fi
    print_success "Docker Compose instalado"
}

# Deploy local
deploy_local() {
    print_info "Iniciando deploy local..."
    
    check_env
    check_dependencies
    
    print_info "Construyendo imágenes..."
    docker-compose build
    
    print_info "Iniciando servicios..."
    docker-compose up -d
    
    print_success "Servicios iniciados"
    print_info "Backend: http://localhost:8000"
    print_info "Frontend: http://localhost:3000"
    print_info "MCP: http://localhost:8080"
    
    print_info "Para ver logs: docker-compose logs -f"
    print_info "Para detener: docker-compose down"
}

# Deploy a Railway
deploy_railway() {
    print_info "Deploy a Railway..."
    
    if ! command -v railway &> /dev/null; then
        print_warning "Railway CLI no instalado"
        print_info "Instala con: npm i -g @railway/cli"
        print_info "O deploy desde: https://railway.app"
        exit 1
    fi
    
    print_info "Asegúrate de haber configurado las variables de entorno en Railway"
    print_info "Presiona Enter para continuar..."
    read
    
    railway up
}

# Build para producción
build_production() {
    print_info "Construyendo imágenes para producción..."
    
    # Backend
    print_info "Construyendo backend..."
    docker build -f Dockerfile.api -t luisito-api:latest .
    
    # Frontend
    print_info "Construyendo frontend..."
    cd chatbot-frontend
    docker build -f Dockerfile -t luisito-frontend:latest .
    cd ..
    
    print_success "Imágenes construidas"
    print_info "Backend: luisito-api:latest"
    print_info "Frontend: luisito-frontend:latest"
}

# Ver estado
status() {
    print_info "Estado de los servicios:"
    docker-compose ps
    
    print_info "\nHealth checks:"
    
    # Backend
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend (port 8000): OK"
    else
        print_error "Backend (port 8000): NO RESPONDE"
    fi
    
    # Frontend
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend (port 3000): OK"
    else
        print_error "Frontend (port 3000): NO RESPONDE"
    fi
    
    # MCP
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        print_success "MCP (port 8080): OK"
    else
        print_error "MCP (port 8080): NO RESPONDE"
    fi
}

# Mostrar ayuda
show_help() {
    echo "Script de deploy para Luisito Comunica Chatbot"
    echo ""
    echo "Uso: ./deploy.sh [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  local           - Deploy local con Docker Compose"
    echo "  build           - Construir imágenes para producción"
    echo "  status          - Verificar estado de servicios"
    echo "  logs            - Ver logs de todos los servicios"
    echo "  stop            - Detener todos los servicios"
    echo "  restart         - Reiniciar todos los servicios"
    echo "  clean           - Limpiar contenedores e imágenes"
    echo "  help            - Mostrar esta ayuda"
    echo ""
    echo "Para deploy en la nube, revisa GUIA_DEPLOY.md"
}

# Main
case "${1:-help}" in
    local)
        deploy_local
        ;;
    build)
        build_production
        ;;
    status)
        status
        ;;
    logs)
        docker-compose logs -f
        ;;
    stop)
        print_info "Deteniendo servicios..."
        docker-compose down
        print_success "Servicios detenidos"
        ;;
    restart)
        print_info "Reiniciando servicios..."
        docker-compose restart
        print_success "Servicios reiniciados"
        ;;
    clean)
        print_warning "Esto eliminará contenedores, imágenes y volúmenes"
        read -p "¿Continuar? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v --rmi all
            print_success "Limpieza completada"
        else
            print_info "Cancelado"
        fi
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Comando desconocido: $1"
        show_help
        exit 1
        ;;
esac

