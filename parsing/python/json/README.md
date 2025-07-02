# Parsing JSON files in Python

## Raw data

Here is a raw *json* file found using *crossref*:

```json
{
  "publisher": "ISTE Group",
  "abstract": "<jats:p>L'objectif principal de la communication véhicule-à-véhicule est d'améliorer la sécurité et l'efficacité routières grâce aux systèmes coopératifs de transport intelligent (C-ITS. Une architecture hybride combinant ITS-G5 et LTE-V2X, optimisée par apprentissage par renforcement, est proposée pour pallier les limites des technologies actuelles et répondre aux exigences croissantes des applications V2X vers une conduite autonome.</jats:p>",
  "DOI": "10.51926/iste.9180.ch4",
  "type": "book-chapter",
  "created": {
    "date-parts": [
      [
        2025,
        5,
        21
      ]
    ],
    "date-time": "2025-05-21T09:15:03Z",
    "timestamp": 1747818903000
  },
  "title": [
    "Hybridation efficace des technologies de communication C-ITS"
  ],
  "author": [
    {
      "given": "Badreddine",
      "family": "Yacine YACHEUR",
      "sequence": "additional",
      "affiliation": []
    },
    {
      "given": "Toufik",
      "family": "AHMED",
      "sequence": "additional",
      "affiliation": []
    },
    {
      "given": "Mohamed",
      "family": "MOSBAH",
      "sequence": "additional",
      "affiliation": []
    }
  ],
  "container-title": [
    "Contrôle et gestion des systèmes de transport intelligents coopératifs"
  ],
  "references-count": 0,
  "URL": "https://doi.org/10.51926/iste.9180.ch4"
}
```

## Classification

The classification only needs:

- The *abstract*, if there is one.

- The *title*.

- The *themes* found, i.e the `container-title`. This one is not
exactly a *theme*, it could the name of an event for which the
publication has been published. Let's consider it is like a title,
and classify it.

Sometimes, there are some *tags* as for instance ``<jats:p>``.
It is necessary to remove them not to add unecessary noises.

### EOF

