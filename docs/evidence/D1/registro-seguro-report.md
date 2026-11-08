# D1 — registro de la corrida automática (seguro-report)

```text
## 1. Preparación (version:1.1.2)
    mirror/ restaurado.
    Listo: C:\Users\GLFRANCO\.tfg-demo\fake_wallet.txt contiene 'DEMO-SEED-NO-ES-REAL'
    ambos modos con la 1.1.2 legítima instalada; seguro con metadatos de confianza al día (disponible en el canal seguro: 1.2.0)

## 2. Ataque
    (el ataque es la publicación por el pipeline: el mirror sirve lo que hay en gh-pages)

## 3. Auditoría (cada control por separado; nunca instala)
- **baseline** · versión ofrecida 1.2.0 → D1-baseline-audit-20261108T154633.json
    ✅ sha256: coincide con latest.json (mismo canal) (0 ms)
    ¿Pasa todos los controles?: sí
- **secure** · versión ofrecida 1.2.0 → D1-seguro-report-audit-20261108T154635.json
    ✅ TUF: metadatos firmados válidos y hashes de los 4 archivos correctos (51 ms)
    ✅ cosign: Verified OK (907 ms)
    ✅ SLSA: PASSED: SLSA verification passed (1095 ms)
    ¿Pasa todos los controles?: sí

## 4. Modo normal (actualizar y jugar)
- **baseline**
    ✅ sha256: coincide con latest.json (mismo canal) (0 ms)
    Instalada la versión 1.2.0. · instalada: 1.2.0
    🚨 El juego ejecutó código malicioso (simulado): PWNED_D1.txt
       | 2026-11-08T15:46:35
       | escenario: D1
       | datos simulados copiados: DEMO-SEED-NO-ES-REAL
- **secure**
    ✅ TUF: metadatos firmados válidos y hashes de los 4 archivos correctos (140 ms)
    ✅ cosign: Verified OK (830 ms)
    ✅ SLSA: PASSED: SLSA verification passed (1113 ms)
    Instalada la versión 1.2.0. · instalada: 1.2.0
    🚨 El juego ejecutó código malicioso (simulado): PWNED_D1.txt
       | 2026-11-08T15:46:43
       | escenario: D1
       | datos simulados copiados: DEMO-SEED-NO-ES-REAL

## 5. Restauración
    mirror/ restaurado.
    Borrado C:\Users\GLFRANCO\.tfg-demo\baseline
    Borrado C:\Users\GLFRANCO\.tfg-demo\secure
    Borrado C:\Users\GLFRANCO\.tfg-demo\PWNED_D1.txt
```
