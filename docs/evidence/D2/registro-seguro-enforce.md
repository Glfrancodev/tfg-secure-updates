# D2 — registro de la corrida automática (seguro-enforce)

```text
## 1. Preparación (version:1.1.2)
    mirror/ restaurado.
    Listo: C:\Users\GLFRANCO\.tfg-demo\fake_wallet.txt contiene 'DEMO-SEED-NO-ES-REAL'
    ambos modos con la 1.1.2 legítima instalada; seguro con metadatos de confianza al día (disponible en el canal seguro: 1.4.0)

## 2. Ataque
    (el ataque es la publicación por el pipeline: el mirror sirve lo que hay en gh-pages)

## 3. Auditoría (cada control por separado; nunca instala)
- **baseline** · versión ofrecida 1.4.0 → D2-baseline-audit-20261108T160737.json
    ✅ sha256: coincide con latest.json (mismo canal) (0 ms)
    ¿Pasa todos los controles?: sí
- **secure** · versión ofrecida 1.4.0 → D2-seguro-enforce-audit-20261108T160740.json
    ✅ TUF: metadatos firmados válidos y hashes de los 4 archivos correctos (198 ms)
    ✅ cosign: Verified OK (916 ms)
    ✅ SLSA: PASSED: SLSA verification passed (1156 ms)
    ¿Pasa todos los controles?: sí

## 4. Modo normal (actualizar y jugar)
- **baseline**
    ✅ sha256: coincide con latest.json (mismo canal) (0 ms)
    Instalada la versión 1.4.0. · instalada: 1.4.0
    🚨 El juego ejecutó código malicioso (simulado): PWNED_D2.txt
       | 2026-11-08T16:07:40
       | escenario: D2
       | datos simulados copiados: DEMO-SEED-NO-ES-REAL
- **secure**
    ✅ TUF: metadatos firmados válidos y hashes de los 4 archivos correctos (140 ms)
    ✅ cosign: Verified OK (832 ms)
    ✅ SLSA: PASSED: SLSA verification passed (1107 ms)
    Instalada la versión 1.4.0. · instalada: 1.4.0
    🚨 El juego ejecutó código malicioso (simulado): PWNED_D2.txt
       | 2026-11-08T16:07:48
       | escenario: D2
       | datos simulados copiados: DEMO-SEED-NO-ES-REAL

## 5. Restauración
    mirror/ restaurado.
    Borrado C:\Users\GLFRANCO\.tfg-demo\baseline
    Borrado C:\Users\GLFRANCO\.tfg-demo\secure
    Borrado C:\Users\GLFRANCO\.tfg-demo\PWNED_D2.txt
```
