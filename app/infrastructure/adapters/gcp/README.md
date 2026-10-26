# Google Cloud Platform (GCP) Adapters

This package is reserved for future Google Cloud Platform database and storage adapters (such as Cloud SQL, Cloud Spanner, Cloud Datastore / Firestore, or Google Cloud Storage).

## Port-Adapter Extension Model
Any GCP database adapter implemented here will fulfill the existing application repository contracts:
- `UserRepositoryPort`
- `PlanRepositoryPort`
- `TrackRepositoryPort`
- `InteractionRepositoryPort`
- `PlaylistRepositoryPort`
- `JamRepositoryPort`
- `ReviewRepositoryPort`

By conforming to the same protocols in `app/application/ports/`, switching between local SQLite and GCP cloud databases is handled purely via dependency injection at the composition root (`app/composition.py`), with zero modifications to application use cases or domain models.
