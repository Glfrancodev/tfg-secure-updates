/*
  Política del juego: el juego no necesita nada fuera de su carpeta.
  Indicadores GENÉRICOS de esa política, buscados en el contenido del artefacto extraído.
  No incluye ninguna cadena propia de un payload concreto.
  Regla CONGELADA desde la Fase 4 (regla 7 del plan): los cambios posteriores se documentan
  como iteración en results/NOTAS.md.
*/

rule game_policy_indicators
{
    meta:
        description = "El artefacto del juego contiene indicadores de acceso a datos del usuario o de ejecución de programas"

    strings:
        $home_path = "Path.home" ascii
        $home_expand = "expanduser" ascii
        $env_userprofile = "USERPROFILE" ascii nocase
        $env_appdata = "APPDATA" ascii nocase
        $exec_subprocess = "subprocess" ascii
        $exec_system = "os.system" ascii
        $data_wallet = "wallet" ascii nocase

    condition:
        any of them
}
