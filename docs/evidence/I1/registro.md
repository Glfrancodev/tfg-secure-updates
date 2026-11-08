# I1 — registro de la corrida automática

```text
## 1. Preparación (previous)
    mirror/ restaurado.
    Listo: C:\Users\GLFRANCO\.tfg-demo\fake_wallet.txt contiene 'DEMO-SEED-NO-ES-REAL'
    ambos modos con la 1.1.0 instalada; seguro con metadatos de confianza al día (disponible 1.1.1)

## 2. Ataque
    baseline: game-1.1.1.zip reemplazado y sha256 recalculado en latest.json
    seguro: game-1.1.1.zip reemplazado (sin claves: los metadatos TUF no cambian)

## 3. Auditoría (cada control por separado; nunca instala)
- **baseline** · versión ofrecida 1.1.1 → I1-baseline-audit-20261108T143200.json
    ✅ sha256: coincide con latest.json (mismo canal) (0 ms)
    ¿Pasa todos los controles?: sí
- **secure** · versión ofrecida 1.1.1 → I1-seguro-enforce-audit-20261108T143202.json
    ❌ TUF: DownloadLengthMismatchError: Downloaded 5861 bytes exceeding the maximum allowed length of 4678 (128 ms)
    ❌ cosign: error during command execution: failed to verify signature: could not verify message: invalid signature when validating ASN.1 encoded signature (838 ms)
    ❌ SLSA: FAILED: SLSA verification failed: expected hash '45d1633f5302186871a9b425d7a14d34261d1506fe465e92591127fa4346e6ad' not found: artifact hash does not match provenance subject (1082 ms)
    ¿Pasa todos los controles?: no

## 4. Modo normal (actualizar y jugar)
- **baseline**
    ✅ sha256: coincide con latest.json (mismo canal) (0 ms)
    Instalada la versión 1.1.1. · instalada: 1.1.1
    🚨 El juego ejecutó código malicioso (simulado): PWNED_I1.txt
       | 2026-11-08T14:32:02
       | escenario: I1
       | datos simulados copiados: DEMO-SEED-NO-ES-REAL
- **secure**
    ❌ TUF: DownloadLengthMismatchError: Downloaded 5861 bytes exceeding the maximum allowed length of 4678 (62 ms)
    TUF rechazó la actualización: no se instala. · instalada: 1.1.0
    Sin marcadores PWNED después de jugar.

## 5. Restauración
    mirror/ restaurado.
    Borrado C:\Users\GLFRANCO\.tfg-demo\baseline
    Borrado C:\Users\GLFRANCO\.tfg-demo\secure
    Borrado C:\Users\GLFRANCO\.tfg-demo\PWNED_I1.txt
```
