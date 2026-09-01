USE finanzas_personales;

INSERT INTO usuarios (id, nombre, email) VALUES
  (1, 'Maria Lopez', 'maria@correo.com'),
  (2, 'Juan Perez', 'juan@correo.com');

INSERT INTO categorias (id_usuario, nombre) VALUES
  (1, 'Salario'), (1, 'Alimentacion'), (1, 'Transporte'),
  (1, 'Entretenimiento'), (1, 'Servicios'),
  (2, 'Salario'), (2, 'Alimentacion'), (2, 'Transporte');

INSERT INTO ingresos_gastos
  (id_usuario, id_categoria, tipo, monto, fecha, descripcion) VALUES
  (1, 1, 'ingreso', 2500000, '2026-01-30', 'Salario enero'),
  (1, 2, 'gasto', 400000, '2026-01-05', 'Mercado quincenal'),
  (1, 3, 'gasto', 120000, '2026-01-10', 'Buses y taxi'),
  (1, 4, 'gasto', 150000, '2026-01-15', 'Cine y salidas'),
  (1, 5, 'gasto', 200000, '2026-01-20', 'Agua y energia'),
  (1, 1, 'ingreso', 2500000, '2026-02-28', 'Salario febrero'),
  (1, 2, 'gasto', 430000, '2026-02-05', 'Mercado mensual'),
  (1, 3, 'gasto', 135000, '2026-02-12', 'Gasolina'),
  (1, 4, 'gasto', 180000, '2026-02-18', 'Concierto'),
  (1, 5, 'gasto', 210000, '2026-02-22', 'Internet y luz'),
  (1, 1, 'ingreso', 2600000, '2026-03-31', 'Salario marzo'),
  (1, 2, 'gasto', 420000, '2026-03-06', 'Supermercado'),
  (1, 3, 'gasto', 140000, '2026-03-11', 'Transporte'),
  (1, 4, 'gasto', 160000, '2026-03-17', 'Salidas'),
  (1, 5, 'gasto', 230000, '2026-03-25', 'Servicios publicos'),
  (1, 2, 'gasto', 950000, '2026-03-13', 'Compra anormal mercado');
