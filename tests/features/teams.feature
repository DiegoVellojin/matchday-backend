Feature: Gestión de Equipos
  Como capitán de un equipo
  Quiero gestionar mis miembros y reclutar nuevos jugadores
  Para mantener la competitividad de mi equipo

  Scenario: Creación exitosa de un equipo
    Given un usuario autenticado como "CapitanX"
    When intento crear un equipo llamado "Los Galácticos" para el deporte 1
    Then el equipo es creado exitosamente
    And yo soy asignado como capitán del equipo

  Scenario: Unirse a un equipo y aceptar solicitud
    Given un usuario autenticado como "CapitanX" con el equipo "Los Galácticos"
    And un usuario autenticado como "JugadorY"
    When "JugadorY" solicita unirse al equipo "Los Galácticos"
    And "CapitanX" acepta la solicitud de "JugadorY"
    Then "JugadorY" debe aparecer en la lista de miembros de "Los Galácticos"
