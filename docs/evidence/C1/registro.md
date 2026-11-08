# C1 — registro de la corrida automática

```text
## 1. Preparación (latest)
    mirror/ restaurado.
    Borrado C:\Users\GLFRANCO\.tfg-demo\baseline
    Borrado C:\Users\GLFRANCO\.tfg-demo\secure
    Listo: C:\Users\GLFRANCO\.tfg-demo\fake_wallet.txt contiene 'DEMO-SEED-NO-ES-REAL'
    baseline: Instalada la versión 1.1.1.
    secure: Instalada la versión 1.1.1.

## 2. Ataque
    zip malicioso: game-9.9.9.zip sha256=9e37087e796885c2…
    baseline: latest.json → 9.9.9 con el hash del zip malicioso
    target game-9.9.9.zip
    target game-9.9.9.zip.sigstore.json
    target game-9.9.9.zip.intoto.jsonl
    target latest.json
    targets v3: 1/2 firmas válidas
    snapshot v3 → targets v3; timestamp v3
    seguro: targets firmado solo con targets-ci; snapshot/timestamp publicados con online

## 3. Auditoría (cada control por separado; nunca instala)
- **baseline** · versión ofrecida 9.9.9 → C1-baseline-audit-20261108T143129.json
    ✅ sha256: coincide con latest.json (mismo canal) (0 ms)
    ¿Pasa todos los controles?: sí
- **secure** · versión ofrecida 9.9.9 → C1-seguro-enforce-audit-20261108T143132.json
    ❌ TUF: UnsignedMetadataError: targets was signed by 1/2 keys (113 ms)
    ❌ cosign: error during command execution: failed to verify signature: could not verify message: invalid signature when validating ASN.1 encoded signature (849 ms)
    ❌ SLSA: FAILED: SLSA verification failed: expected hash '9e37087e796885c2aa0e5ca0284afac5de324954b16dabd05bb143a46586499b' not found: artifact hash does not match provenance subject (1093 ms)
    ¿Pasa todos los controles?: no

## 4. Modo normal (actualizar y jugar)
- **baseline**
    ✅ sha256: coincide con latest.json (mismo canal) (0 ms)
    Instalada la versión 9.9.9. · instalada: 9.9.9
    🚨 El juego ejecutó código malicioso (simulado): PWNED_C1.txt
       | 2026-11-08T14:31:32
       | escenario: C1
       | datos simulados copiados: DEMO-SEED-NO-ES-REAL
- **secure**
    ❌ TUF: UnsignedMetadataError: targets was signed by 1/2 keys (102 ms)
    TUF rechazó la actualización: no se instala. · instalada: 1.1.1
    Sin marcadores PWNED después de jugar.

## 5. Restauración
    mirror/ restaurado.
    Borrado C:\Users\GLFRANCO\.tfg-demo\baseline
    Borrado C:\Users\GLFRANCO\.tfg-demo\secure
    Borrado C:\Users\GLFRANCO\.tfg-demo\PWNED_C1.txt
```
