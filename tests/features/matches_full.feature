Feature: Ciclo de Vida de Partidos
  Como jugador de fútbol
  Quiero organizar y participar en partidos
  Para competir y mejorar mi ranking

  Scenario: Publicación de un nuevo partido
    Given un usuario autenticado como "OrganizadorA"
    When intento publicar un partido para el deporte 1 en la cancha 1
    Then el partido aparece en el feed como "publicada"

  Scenario: Unirse individualmente a un partido
    Given un partido publicado por "OrganizadorA"
    And un usuario autenticado como "JugadorIndividual"
    When "JugadorIndividual" intenta unirse al partido
    Then "JugadorIndividual" debe estar en la lista de jugadores del partido

  Scenario: Registro y confirmación de resultados
    Given un partido en estado "confirmada" entre "EquipoA" y "EquipoB"
    When el capitán de "EquipoA" registra un resultado de 2-1
    And el capitán de "EquipoB" registra un resultado de 2-1
    Then el partido debe cambiar a estado "completada"
    And el ranking de los equipos debe actualizarse
