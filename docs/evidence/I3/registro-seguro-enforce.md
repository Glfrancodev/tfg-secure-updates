# I3 — registro de la corrida automática (seguro-enforce)

```text
## 1. Preparación (version:1.1.2)
    mirror/ restaurado.
    Listo: C:\Users\GLFRANCO\.tfg-demo\fake_wallet.txt contiene 'DEMO-SEED-NO-ES-REAL'
    ambos modos con la 1.1.2 legítima instalada; seguro con metadatos de confianza al día (disponible en el canal seguro: 1.1.2)

## 2. Ataque
    (el ataque es la publicación por el pipeline: el mirror sirve lo que hay en gh-pages)

## 3. Auditoría (cada control por separado; nunca instala)
- **baseline** · versión ofrecida 1.3.0 → I3-baseline-audit-20261108T155225.json
    ✅ sha256: coincide con latest.json (mismo canal) (0 ms)
    ¿Pasa todos los controles?: sí
- **secure** · versión ofrecida 1.1.2 → I3-seguro-enforce-audit-20261108T155227.json
    ✅ TUF: metadatos firmados válidos y hashes de los 4 archivos correctos (188 ms)
    ✅ cosign: Verified OK (990 ms)
    ✅ SLSA: PASSED: SLSA verification passed (1119 ms)
    ¿Pasa todos los controles?: sí

## 4. Modo normal (actualizar y jugar)
- **baseline**
    ✅ sha256: coincide con latest.json (mismo canal) (0 ms)
    Instalada la versión 1.3.0. · instalada: 1.3.0
    🚨 El juego ejecutó código malicioso (simulado): PWNED_I3.txt
       | 2026-11-08T15:52:27
       | escenario: I3
       | datos simulados copiados: DEMO-SEED-NO-ES-REAL
- **secure**
    ✅ TUF: metadatos firmados válidos y hashes de los 4 archivos correctos (84 ms)
    Ya está instalada la versión publicada (1.1.2). · instalada: 1.1.2
    Sin marcadores PWNED después de jugar.

## 5. Restauración
    mirror/ restaurado.
    Borrado C:\Users\GLFRANCO\.tfg-demo\baseline
    Borrado C:\Users\GLFRANCO\.tfg-demo\secure
    Borrado C:\Users\GLFRANCO\.tfg-demo\PWNED_I3.txt
```
