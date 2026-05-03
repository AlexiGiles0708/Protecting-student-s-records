SELECT u.nombre_completo, u.username, u.rol, u.id_estatus,
       e.calle, e.colonia, e.codigo_postal, e.telefono, e.fecha_nacimiento
FROM Usuario u
    JOIN Estudiante e ON u.id_usuario = e.id_usuario

-- Eliminar usuarios

-- Insertar director

insert into Usuario (nombre_completo, username, rol, id_estatus, contrasena)
values ('Juan Pérez', 'juanperez', 'estudiante', 1, '$2b$12$5YRm5PXtn0T2pNGpZBT6JeiHOtu4LJOzlq6E1nRcgbjU.5dOiasfG');



SELECT * FROM Usuario

SELECT u.id_usuario,u.nombre_completo, u.username, u.rol,
                   e.calle, e.colonia, e.codigo_postal, e.telefono, e.fecha_nacimiento
            FROM Usuario u
                JOIN Estudiante e ON u.id_usuario = e.id_usuario

select * from auditoria
            


