from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import logging

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Variables globales
SERVICE_NAME = os.getenv('SERVICE_NAME', 'Sistema de Préstamo de Libros')
SERVICE_VERSION = os.getenv('SERVICE_VERSION', '1.0.0')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Configuración de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///libros.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelos de datos
class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False, unique=True)
    autor = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True)
    cantidad_total = db.Column(db.Integer, default=1)
    cantidad_disponible = db.Column(db.Integer, default=1)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    prestamos = db.relationship('Loan', backref='libro', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'autor': self.autor,
            'isbn': self.isbn,
            'cantidad_total': self.cantidad_total,
            'cantidad_disponible': self.cantidad_disponible,
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'prestamos_activos': len([p for p in self.prestamos if not p.devuelto])
        }

class Loan(db.Model):
    __tablename__ = 'loans'
    
    id = db.Column(db.Integer, primary_key=True)
    libro_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    usuario_nombre = db.Column(db.String(100), nullable=False)
    usuario_email = db.Column(db.String(100), nullable=False)
    fecha_prestamo = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_vencimiento = db.Column(db.DateTime, nullable=False)
    fecha_devolucion = db.Column(db.DateTime)
    devuelto = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'libro_id': self.libro_id,
            'libro_titulo': self.libro.titulo,
            'usuario_nombre': self.usuario_nombre,
            'usuario_email': self.usuario_email,
            'fecha_prestamo': self.fecha_prestamo.isoformat(),
            'fecha_vencimiento': self.fecha_vencimiento.isoformat(),
            'fecha_devolucion': self.fecha_devolucion.isoformat() if self.fecha_devolucion else None,
            'devuelto': self.devuelto,
            'dias_restantes': (self.fecha_vencimiento - datetime.utcnow()).days if not self.devuelto else 0
        }

# Crear tablas
with app.app_context():
    db.create_all()

# ==================== SALUD Y INFO ====================

# Variable para controlar si ya se inicializó
_initialized = False

def initialize_db():
    """Inicializar base de datos con datos de muestra"""
    global _initialized
    if _initialized:
        return
    
    try:
        # Verificar si ya hay libros
        if Book.query.count() > 0:
            _initialized = True
            return
        
        # Crear libros de muestra
        books = [
            Book(titulo='Don Quijote', autor='Miguel de Cervantes', isbn='978-84-376-0494-1', cantidad_total=5, cantidad_disponible=5),
            Book(titulo='1984', autor='George Orwell', isbn='978-0451524935', cantidad_total=3, cantidad_disponible=3),
            Book(titulo='El Gran Gatsby', autor='F. Scott Fitzgerald', isbn='978-0743273565', cantidad_total=4, cantidad_disponible=4),
            Book(titulo='Orgullo y Prejuicio', autor='Jane Austen', isbn='978-0141439518', cantidad_total=2, cantidad_disponible=2),
            Book(titulo='El Código Da Vinci', autor='Dan Brown', isbn='978-0307474278', cantidad_total=3, cantidad_disponible=2),
            Book(titulo='Harry Potter', autor='J.K. Rowling', isbn='978-0747532699', cantidad_total=5, cantidad_disponible=4),
            Book(titulo='Cien años de soledad', autor='Gabriel García Márquez', isbn='978-0-06-088328-7', cantidad_total=2, cantidad_disponible=1),
            Book(titulo='Fahrenheit 451', autor='Ray Bradbury', isbn='978-1451673265', cantidad_total=3, cantidad_disponible=3),
        ]
        
        for book in books:
            db.session.add(book)
        
        db.session.commit()
        
        # Crear préstamos de muestra
        libro1 = Book.query.filter_by(titulo='Don Quijote').first()
        libro2 = Book.query.filter_by(titulo='1984').first()
        
        if libro1:
            prestamo1 = Loan(
                libro_id=libro1.id,
                usuario_nombre='Juan Pérez',
                usuario_email='juan@example.com',
                fecha_prestamo=datetime.utcnow() - timedelta(days=10),
                fecha_vencimiento=datetime.utcnow() + timedelta(days=4)
            )
            db.session.add(prestamo1)
            libro1.cantidad_disponible -= 1
        
        if libro2:
            prestamo2 = Loan(
                libro_id=libro2.id,
                usuario_nombre='María García',
                usuario_email='maria@example.com',
                fecha_prestamo=datetime.utcnow() - timedelta(days=5),
                fecha_vencimiento=datetime.utcnow() + timedelta(days=9)
            )
            db.session.add(prestamo2)
            libro2.cantidad_disponible -= 1
        
        db.session.commit()
        logger.info('✓ Base de datos inicializada con datos de muestra')
        _initialized = True
    except Exception as e:
        logger.error(f'Error inicializando BD: {e}')
        _initialized = True

@app.before_request
def before_request():
    """Ejecutar antes de cada request"""
    initialize_db()

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de healthcheck para balanceadores de carga"""
    return jsonify({
        'status': 'healthy',
        'service': SERVICE_NAME,
        'version': SERVICE_VERSION,
        'environment': ENVIRONMENT
    }), 200

@app.route('/api/info', methods=['GET'])
def info():
    """Endpoint de información del servicio"""
    return jsonify({
        'name': SERVICE_NAME,
        'version': SERVICE_VERSION,
        'environment': ENVIRONMENT,
        'description': 'Sistema de Préstamo de Libros'
    }), 200

# ==================== LIBROS ====================

@app.route('/api/libros', methods=['GET'])
def get_libros():
    """Obtener todos los libros"""
    try:
        libros = Book.query.all()
        return jsonify({
            'total': len(libros),
            'libros': [libro.to_dict() for libro in libros]
        }), 200
    except Exception as e:
        logger.error(f'Error al obtener libros: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/libros/<int:libro_id>', methods=['GET'])
def get_libro(libro_id):
    """Obtener un libro por ID"""
    try:
        libro = Book.query.get_or_404(libro_id)
        return jsonify(libro.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Libro no encontrado'}), 404

@app.route('/api/libros', methods=['POST'])
def crear_libro():
    """Crear un nuevo libro"""
    try:
        datos = request.get_json()
        
        # Validar datos requeridos
        if not datos or not datos.get('titulo') or not datos.get('autor'):
            return jsonify({'error': 'Título y autor son requeridos'}), 400
        
        # Validar que el libro no exista
        libro_existente = Book.query.filter_by(titulo=datos['titulo']).first()
        if libro_existente:
            return jsonify({'error': 'El libro ya existe'}), 409
        
        nuevo_libro = Book(
            titulo=datos['titulo'],
            autor=datos['autor'],
            isbn=datos.get('isbn'),
            cantidad_total=datos.get('cantidad_total', 1),
            cantidad_disponible=datos.get('cantidad_total', 1)
        )
        
        db.session.add(nuevo_libro)
        db.session.commit()
        
        logger.info(f'Libro creado: {nuevo_libro.titulo}')
        return jsonify(nuevo_libro.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error al crear libro: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/libros/<int:libro_id>', methods=['PUT'])
def actualizar_libro(libro_id):
    """Actualizar un libro"""
    try:
        libro = Book.query.get_or_404(libro_id)
        datos = request.get_json()
        
        if 'titulo' in datos:
            libro.titulo = datos['titulo']
        if 'autor' in datos:
            libro.autor = datos['autor']
        if 'isbn' in datos:
            libro.isbn = datos['isbn']
        if 'cantidad_total' in datos:
            libro.cantidad_total = datos['cantidad_total']
        
        db.session.commit()
        logger.info(f'Libro actualizado: {libro.titulo}')
        return jsonify(libro.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error al actualizar libro: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/libros/<int:libro_id>', methods=['DELETE'])
def eliminar_libro(libro_id):
    """Eliminar un libro"""
    try:
        libro = Book.query.get_or_404(libro_id)
        titulo = libro.titulo
        db.session.delete(libro)
        db.session.commit()
        logger.info(f'Libro eliminado: {titulo}')
        return jsonify({'mensaje': f'Libro {titulo} eliminado'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error al eliminar libro: {e}')
        return jsonify({'error': str(e)}), 500

# ==================== PRÉSTAMOS ====================

@app.route('/api/prestamos', methods=['GET'])
def get_prestamos():
    """Obtener todos los préstamos"""
    try:
        activos = request.args.get('activos', 'false').lower() == 'true'
        
        if activos:
            prestamos = Loan.query.filter_by(devuelto=False).all()
        else:
            prestamos = Loan.query.all()
        
        return jsonify({
            'total': len(prestamos),
            'prestamos': [prestamo.to_dict() for prestamo in prestamos]
        }), 200
    except Exception as e:
        logger.error(f'Error al obtener préstamos: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/prestamos', methods=['POST'])
def crear_prestamo():
    """Crear un nuevo préstamo"""
    try:
        datos = request.get_json()
        
        # Validar datos requeridos
        requeridos = ['libro_id', 'usuario_nombre', 'usuario_email']
        if not datos or not all(k in datos for k in requeridos):
            return jsonify({'error': f'Campos requeridos: {", ".join(requeridos)}'}), 400
        
        # Verificar que el libro existe
        libro = Book.query.get_or_404(datos['libro_id'])
        
        # Verificar disponibilidad
        if libro.cantidad_disponible <= 0:
            return jsonify({'error': 'No hay copias disponibles'}), 409
        
        # Crear préstamo
        dias_prestamo = datos.get('dias_prestamo', 14)
        fecha_vencimiento = datetime.utcnow() + timedelta(days=dias_prestamo)
        
        nuevo_prestamo = Loan(
            libro_id=datos['libro_id'],
            usuario_nombre=datos['usuario_nombre'],
            usuario_email=datos['usuario_email'],
            fecha_vencimiento=fecha_vencimiento
        )
        
        # Actualizar disponibilidad
        libro.cantidad_disponible -= 1
        
        db.session.add(nuevo_prestamo)
        db.session.commit()
        
        logger.info(f'Préstamo creado: {libro.titulo} para {datos["usuario_nombre"]}')
        return jsonify(nuevo_prestamo.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error al crear préstamo: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/prestamos/<int:prestamo_id>/devolver', methods=['POST'])
def devolver_libro(prestamo_id):
    """Devolver un libro (marcar como devuelto)"""
    try:
        prestamo = Loan.query.get_or_404(prestamo_id)
        
        if prestamo.devuelto:
            return jsonify({'error': 'El libro ya fue devuelto'}), 409
        
        # Registrar devolución
        prestamo.devuelto = True
        prestamo.fecha_devolucion = datetime.utcnow()
        
        # Liberar copia del libro
        prestamo.libro.cantidad_disponible += 1
        
        # Calcular multa si fue devuelto tarde
        dias_retraso = (datetime.utcnow() - prestamo.fecha_vencimiento).days
        multa = max(0, dias_retraso * 2) if dias_retraso > 0 else 0  # $2 por día de retraso
        
        db.session.commit()
        
        logger.info(f'Libro devuelto: {prestamo.libro.titulo} por {prestamo.usuario_nombre}')
        return jsonify({
            **prestamo.to_dict(),
            'multa': f'${multa}' if multa > 0 else 'Sin multa',
            'dias_retraso': max(0, dias_retraso)
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error al devolver libro: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/prestamos/usuario/<usuario_email>', methods=['GET'])
def get_prestamos_usuario(usuario_email):
    """Obtener préstamos de un usuario específico"""
    try:
        prestamos = Loan.query.filter_by(usuario_email=usuario_email).all()
        
        if not prestamos:
            return jsonify({'error': 'No hay préstamos para este usuario'}), 404
        
        return jsonify({
            'total': len(prestamos),
            'usuario_email': usuario_email,
            'prestamos': [p.to_dict() for p in prestamos]
        }), 200
    except Exception as e:
        logger.error(f'Error al obtener préstamos del usuario: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/estadisticas', methods=['GET'])
def estadisticas():
    """Obtener estadísticas de la biblioteca"""
    try:
        total_libros = Book.query.count()
        total_copias = db.session.query(db.func.sum(Book.cantidad_total)).scalar() or 0
        copias_disponibles = db.session.query(db.func.sum(Book.cantidad_disponible)).scalar() or 0
        prestamos_activos = Loan.query.filter_by(devuelto=False).count()
        prestamos_vencidos = Loan.query.filter(
            Loan.devuelto == False,
            Loan.fecha_vencimiento < datetime.utcnow()
        ).count()
        
        return jsonify({
            'total_libros': total_libros,
            'total_copias': total_copias,
            'copias_disponibles': copias_disponibles,
            'copias_prestadas': total_copias - copias_disponibles,
            'prestamos_activos': prestamos_activos,
            'prestamos_vencidos': prestamos_vencidos
        }), 200
    except Exception as e:
        logger.error(f'Error al calcular estadísticas: {e}')
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Manejo de rutas no encontradas"""
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejo de errores internos"""
    logger.error(f'Error interno: {error}')
    return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== INICIALIZACIÓN ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False') == 'True'
    app.run(host='0.0.0.0', port=port, debug=debug)
