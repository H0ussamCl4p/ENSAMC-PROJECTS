# J-SOC — Java Security Operations Center

Application console de gestion d'incidents de sécurité, développée dans le cadre du module de **Programmation Orientée Objet en Java**.

## Description

J-SOC permet à une équipe SOC de suivre le cycle de vie complet d'incidents de sécurité (phishing, malware, DDoS) : création, assignation, traitement, résolution et clôture. Le projet met en pratique les concepts POO (héritage, polymorphisme, classes abstraites, interfaces, exceptions) avec une persistance en fichiers CSV et une interface en ligne de commande.

## Démarrage

Compilation (PowerShell) :
```powershell
javac -d out (Get-ChildItem -Recurse -Filter *.java -Path src/main/java | Select-Object -ExpandProperty FullName)
```

Exécution :
```bash
java -cp out jsoc.Main
```

## Comptes par défaut

| Username | Password | Rôle |
|---|---|---|
| `alice` | `password` | Analyst |
| `bob` | `password` | Analyst |
| `carol` | `password` | Manager |

## Stack

Java 17+ — aucune dépendance externe — persistance CSV.

## Documentation

Le diagramme de classes complet est disponible dans `docs/UML.puml`.

---

## Réalisé par

- **CHOUBIK Houssam**
- **NAATANI Fouad**
- **BOULANOUAR Yasser**
- **MARZAK Amine**

*POO Java & UML — Année universitaire 2025/2026*
