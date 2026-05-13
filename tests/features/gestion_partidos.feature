Feature: Gestión y Negociación de Partidos
  Como capitán de un equipo
  Quiero proponer y aceptar términos de un partido
  Para que el encuentro pase a estado pendiente de pago

  Scenario: Acuerdo exitoso de términos entre capitanes
    Given un partido publicado con el organizador "CapitanA"
    And un equipo retador liderado por "CapitanB"
    When "CapitanB" propone jugar el "2026-06-01" con un costo total de 100
    And "CapitanA" acepta la propuesta con los mismos términos
    Then el estatus del partido debe cambiar a "pendiente_pago"
    And el costo total en la base de datos debe ser 100
