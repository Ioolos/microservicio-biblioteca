#!/usr/bin/env powershell
# Script de testing para el sistema de préstamo de libros

$API_URL = "http://127.0.0.1:5000"

Write-Host "=== Testing Sistema de Préstamo de Libros ===" -ForegroundColor Blue
Write-Host ""

function Make-Request {
    param(
        [string]$Method = "GET",
        [string]$Endpoint,
        [hashtable]$Body
    )
    
    $Uri = "$API_URL$Endpoint"
    
    try {
        if ($Body) {
            $Response = Invoke-WebRequest -Uri $Uri -Method $Method -Body ($Body | ConvertTo-Json) -ContentType "application/json" -UseBasicParsing
        } else {
            $Response = Invoke-WebRequest -Uri $Uri -Method $Method -UseBasicParsing
        }
        
        $Response.Content | ConvertFrom-Json | ConvertTo-Json
    } catch {
        Write-Host "Error: $_" -ForegroundColor Red
    }
}

# Pruebas
Write-Host "1. Health Check:" -ForegroundColor Green
Make-Request -Endpoint "/health"

Write-Host "`n2. Información del Servicio:" -ForegroundColor Green
Make-Request -Endpoint "/api/info"

Write-Host "`n3. Obtener todos los libros:" -ForegroundColor Green
Make-Request -Endpoint "/api/libros"

Write-Host "`n4. Obtener estadísticas:" -ForegroundColor Green
Make-Request -Endpoint "/api/estadisticas"

Write-Host "`n5. Obtener préstamos activos:" -ForegroundColor Green
Make-Request -Endpoint "/api/prestamos?activos=true"

Write-Host "`n6. Crear un nuevo libro:" -ForegroundColor Green
$NewBook = @{
    titulo = "El Quijote"
    autor = "Miguel de Cervantes"
    isbn = "978-8491810254"
    cantidad_total = 2
}
Make-Request -Method "POST" -Endpoint "/api/libros" -Body $NewBook

Write-Host "`n✅ Tests completados" -ForegroundColor Green
