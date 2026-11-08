# I2 — registro de la corrida automática

```text
## 1. Preparación (latest)
    mirror/ restaurado.
    Listo: C:\Users\GLFRANCO\.tfg-demo\fake_wallet.txt contiene 'DEMO-SEED-NO-ES-REAL'
    baseline: Instalada la versión 1.1.2.
    secure: Instalada la versión 1.1.2.

## 2. Ataque
    baseline: se sirve el estado de 781173f → 1.0.0
    seguro: se sirve el estado de f549287 → 1.1.1 (metadatos TUF de esa publicación)

## 3. Auditoría (cada control por separado; nunca instala)
- **baseline** · versión ofrecida 1.0.0 → I2-baseline-audit-20261108T151725.json
    ✅ sha256: coincide con latest.json (mismo canal) (0 ms)
    ¿Pasa todos los controles?: sí
- **secure** · versión ofrecida 1.1.1 → I2-seguro-enforce-audit-20261108T151727.json
    ❌ TUF: BadVersionNumberError: New timestamp version 2 must be >= 3 (33 ms)
    ✅ cosign: Verified OK (822 ms)
    ✅ SLSA: PASSED: SLSA verification passed (1116 ms)
    ¿Pasa todos los controles?: no

## 4. Modo normal (actualizar y jugar)
- **baseline**
    ✅ sha256: coincide con latest.json (mismo canal) (0 ms)
    Instalada la versión 1.0.0. · instalada: 1.0.0
    Sin marcadores PWNED después de jugar.
- **secure**
    ❌ TUF: BadVersionNumberError: New timestamp version 2 must be >= 3 (37 ms)
    TUF rechazó la actualización: no se instala. · instalada: 1.1.2
    Sin marcadores PWNED después de jugar.

## 5. Restauración
    mirror/ restaurado.
    Borrado C:\Users\GLFRANCO\.tfg-demo\baseline
    Borrado C:\Users\GLFRANCO\.tfg-demo\secure
```
