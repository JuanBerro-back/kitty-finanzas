USE finanzas_personales;

-- Ejecutar SOLO si ya existía la tabla usuarios con el esquema anterior (sin email).
-- Agrega los campos necesarios para login/registro y cuenta de Google.
ALTER TABLE usuarios
  ADD COLUMN email VARCHAR(180) NOT NULL DEFAULT '' AFTER nombre,
  ADD COLUMN password_hash VARCHAR(255) NULL AFTER email,
  ADD COLUMN google_id VARCHAR(100) NULL AFTER password_hash,
  ADD COLUMN avatar VARCHAR(500) NULL AFTER google_id,
  ADD UNIQUE KEY uq_email (email),
  ADD UNIQUE KEY uq_google (google_id);
