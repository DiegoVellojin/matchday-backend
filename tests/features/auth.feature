Feature: Autenticación de Usuarios
  Como jugador de MatchDay
  Quiero registrarme e iniciar sesión
  Para poder participar en equipos y partidos

  Scenario: Registro exitoso de un nuevo usuario
    Given que el correo "nuevo@test.com" no está registrado
    When intento registrarme con nombre "Jugador Nuevo", correo "nuevo@test.com" y contraseña "Pass123!"
    Then el registro es exitoso
    And recibo un token de acceso válido

  Scenario: Inicio de sesión exitoso
    Given un usuario registrado con correo "login@test.com" y contraseña "Secret123"
    When intento iniciar sesión con correo "login@test.com" y contraseña "Secret123"
    Then el inicio de sesión es exitoso
    And recibo un token de acceso válido

  Scenario: Intento de inicio de sesión con contraseña incorrecta
    Given un usuario registrado con correo "login@test.com" y contraseña "Secret123"
    When intento iniciar sesión con correo "login@test.com" y contraseña "WrongPass"
    Then recibo un error de "credenciales inválidas"
