"""Script para inicializar la base de datos con datos de ejemplo"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.app import app, db, Book, Loan
from datetime import datetime, timedelta

def init_database():
    """Crear y rellenar la base de datos con datos de ejemplo"""
    
    with app.app_context():
        # Eliminar tablas existentes (solo para demo)
        # db.drop_all()
        
        # Crear tablas
        db.create_all()
        
        # Verificar si ya hay libros
        if Book.query.first():
            print("✓ La base de datos ya tiene datos")
            return
        
        # Crear libros de ejemplo
        libros_ejemplo = [
            {
                'titulo': 'Cien años de soledad',
                'autor': 'Gabriel García Márquez',
                'isbn': '978-8401042015',
                'cantidad_total': 3
            },
            {
                'titulo': 'Don Quijote',
                'autor': 'Miguel de Cervantes',
                'isbn': '978-8491810254',
                'cantidad_total': 2
            },
            {
                'titulo': '1984',
                'autor': 'George Orwell',
                'isbn': '978-0451524935',
                'cantidad_total': 3
            },
            {
                'titulo': 'El Principito',
                'autor': 'Antoine de Saint-Exupéry',
                'isbn': '978-8430742646',
                'cantidad_total': 4
            },
            {
                'titulo': 'Harry Potter y la Piedra Filosofal',
                'autor': 'J.K. Rowling',
                'isbn': '978-8432715951',
                'cantidad_total': 2
            },
            {
                'titulo': 'Orgullo y Prejuicio',
                'autor': 'Jane Austen',
                'isbn': '978-8432715234',
                'cantidad_total': 2
            },
            {
                'titulo': 'El Gran Gatsby',
                'autor': 'F. Scott Fitzgerald',
                'isbn': '978-8491051268',
                'cantidad_total': 3
            },
            {
                'titulo': 'Matar a un ruiseñor',
                'autor': 'Harper Lee',
                'isbn': '978-8432715302',
                'cantidad_total': 2
            }
        ]
        
        print("📚 Creando libros...")
        for libro_data in libros_ejemplo:
            libro = Book(
                titulo=libro_data['titulo'],
                autor=libro_data['autor'],
                isbn=libro_data['isbn'],
                cantidad_total=libro_data['cantidad_total'],
                cantidad_disponible=libro_data['cantidad_total']
            )
            db.session.add(libro)
        
        db.session.commit()
        print(f"✓ {len(libros_ejemplo)} libros creados")
        
        # Crear préstamos de ejemplo
        print("📖 Creando préstamos de ejemplo...")
        
        usuarios_ejemplo = [
            {'nombre': 'Juan Pérez', 'email': 'juan@example.com'},
            {'nombre': 'María García', 'email': 'maria@example.com'},
            {'nombre': 'Carlos López', 'email': 'carlos@example.com'},
        ]
        
        libros = Book.query.all()
        prestamo_count = 0
        
        for idx, usuario in enumerate(usuarios_ejemplo):
            if idx < len(libros):
                libro = libros[idx]
                fecha_vencimiento = datetime.utcnow() + timedelta(days=14)
                
                prestamo = Loan(
                    libro_id=libro.id,
                    usuario_nombre=usuario['nombre'],
                    usuario_email=usuario['email'],
                    fecha_vencimiento=fecha_vencimiento
                )
                db.session.add(prestamo)
                libro.cantidad_disponible -= 1
                prestamo_count += 1
        
        db.session.commit()
        print(f"✓ {prestamo_count} préstamos creados")
        
        print("\n✅ Base de datos inicializada correctamente")
        print("\nEstadísticas:")
        print(f"  - Total de libros: {Book.query.count()}")
        print(f"  - Préstamos activos: {Loan.query.filter_by(devuelto=False).count()}")

if __name__ == '__main__':
    init_database()
