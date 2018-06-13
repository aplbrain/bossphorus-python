# Features

One of the goals of Bossphorus is to approximate feature-parity with bossDB. There are many endpoints that we do not anticipate emulating: These are marked with a dot to indicate that they are not on the roadmap for this project. If your work relies upon one of these endpoints or capabilities, please get in touch by filing an Issue.

In particular, **we do not plan to implement authentication or permissions logic**.

---

| Won't Implement | On Roadmap | In Progress | Complete |
|-----------------|------------|-------------|----------|
| •               | ⛔         | ⌛           | ✅ ️      |


| Endpoint | Status | Notes |
|----------|--------|-------|
| **GET**  `/sso/user/:user_name` | ️• | |
| **POST**  `/sso/user/:user_name` | ️• | |
| **DELETE**  `/sso/user/:user_name` | ️• | |
| **GET**  `/sso/user-role/:user_name/:role_name` | ️• | |
| **POST**  `/sso/user-role/:user_name/:role_name` | ️• | |
| **DELETE**  `/sso/user-role/:user_name/:role_name` | ️• | |
| **GET**  `/collection/` | ️⛔ | |
| **GET**  `/collection/:collection/experiment/` | ️⛔ | |
| **GET**  `/collection/:collection/experiment/:experiment/channel/` | ️⛔ | |
| **GET**  `/coord/` | ️• | |
| **POST**  `/collection/:collection/` | ️⛔ | |
| **POST**  `/collection/:collection/experiment/:experiment/` | ️⛔ | |
| **POST**  `/collection/:collection/experiment/:experiment/channel/:channel/` | ️⛔ | |
| **POST**  `/coord/:coordinate_frame` | ️• | |
| **GET**  `/collection/:collection` | ️⛔ | |
| **GET**  `/collection/:collection/experiment/:experiment/` | ️⛔ | |
| **GET**  `/collection/:collection/experiment/:experiment/channel/:channel/` | ️✅ | |
| **GET**  `/coord/:coordinate_frame` | ️• | |
| **PUT**  `/collection/:collection` | ️⛔ | |
| **PUT**  `/collection/:collection/experiment/:experiment/` | ️⛔ | |
| **PUT**  `/collection/:collection/experiment/:experiment/channel/:channel/` | ️⛔ | |
| **PUT**  `/coord/:coordinate_frame` | ️• | |
| **DELETE**  `/collection/:collection` | ️• | |
| **DELETE**  `/collection/:collection/experiment/:experiment/` | ️• | |
| **DELETE**  `/collection/:collection/experiment/:experiment/channel/:channel/` | ️• | |
| **DELETE**  `/coord/:coordinate_frame` | ️• | |
| **GET**  `/groups/` | ️• | |
| **GET**  `/groups/:group_name` | ️• | |
| **POST**  `/groups/:group_name` | ️• | |
| **DELETE**  `/groups/:group_name` | ️• | |
| **GET**  `/groups/:group_name/members` | ️• | |
| **POST**  `/groups/:group_name/members/:user_name` | ️• | |
| **DELETE**  `/groups/:group_name/members/:user_name` | ️• | |
| **GET**  `/groups/:groupname/members/:username` | ️• | |
| **GET**  `/groups/:group_name/maintainers` | ️• | |
| **POST**  `/groups/:group_name/maintainers/:user_name` | ️• | |
| **DELETE**  `/groups/:group_name/maintainers/:user_name` | ️• | |
| **GET**  `/groups/:groupname/maintianers/:username` | ️• | |
| **GET**  `/permissions/` | ️• | |
| **POST**  `/permissions/` | ️• | |
| **`patch** /permissions/` | ️• | |
| **DELETE**  `/permissions/:group_name/:collection` | ️• | |
| **POST**  `/cutout/:collection/:experiment/:channel/:resolution/:x_range/:y_range/:z_range/:time_range/?iso=:iso` | ️✅ | Supports 3D (not 4D) data |
| **GET**  `/cutout/:collection/:experiment/:channel/:resolution/:x_range/:y_range/:z_range/:time_range?iso=:iso` | ️⌛️ | Supports `blosc` cutouts |
| **GET**  `/reserve/:collection/:experiment/:channel/:num_ids` | ️• | |
| **GET**  `/ids/:collection/:experiment/:channel/:resolution/:x_range/:y_range/:z_range/:time_range/` | ️⛔️ | |
| **GET**  `/boundingbox/:collection/:experiment/:channel/:ids` | ️• | |
| **GET**  `/image/:collection/:experiment/:channel/:orientation/:resolution/:x_arg/:y_arg/:z_arg/:t_index/` | ️⌛ | |
| **GET**  `/tile/:collection/:experiment/:channel/:orientation/:tile_size/:resolution/:x_idx/:y_idx/:z_idx/:t_idx/` | ️⌛ | |
| **GET**  `/downsample/:collection/:experiment/:channel?iso=:iso` | ️• | |
| **GET**  `/downsample/:collection/:experiment/:channel` | ️• | |
| **GET**  `/downsample/:collection/:experiment/:channel` | ️• | |
| **GET**  `/meta/:collection/?key=:key` | ️• | |
| **GET**  `/meta/:collection/:experiment/?key=:key` | ️⛔ | |
| **GET**  `/meta/:collection/:experiment/:channel/?key=:key` | ️⛔ | |
| **POST**  `/meta/:collection/?key=:key&value=:value` | ️⛔ | |
| **POST**  `/meta/:collection/:experiment/?key=:key&value=:value` | ️⛔ | |
| **POST**  `/meta/:collection/:experiment/:channel/?key=:key&value=:value` | ️⛔ | |
| **PUT**  `/meta/:collection/?key=:key&value=:value` | ️⛔ | |
| **PUT**  `/meta/:collection/:experiment/?key=:key&value=:value` | ️⛔ | |
| **PUT**  `/meta/:collection/:experiment/:channel/?key=:key&value=:value` | ️⛔ | |
| **DELETE**  `/meta/:collection/?key=:key` | ️⛔ | |
| **DELETE**  `/meta/:collection/:experiment/?key=:key` | ️⛔ | |
| **DELETE**  `/meta/:collection/:experiment/:channel/?key=:key` | ️⛔ | |
| **GET**  `/ingest/` | ️• | |
| **GET**  `/ingest/:job_id` | ️• | |
| **POST**  `/ingest/` | ️• | |
| **GET**  `/ingest/:job_id/status` | ️• | |
| **DELETE**  `/ingest/:job_id` | ️• | |
| **POST**  `/ingest/:job_id/complete` | ️• | |
