# Deployment boundary

The API image contains runtime code, assistant resources and report snapshots.
It excludes training/evaluation code, datasets, checkpoints, developer dependencies,
Git history, secrets, test fixtures and caches. It uses CPU PyTorch and local TFLite.
Mount approved weights separately; source-only startup reports unavailable models
until those files exist. Vertex remains disabled unless explicitly configured.

From the repository root:

```powershell
docker build -f deploy/Dockerfile.api -t steel-defect-api .
docker run --rm -p 8001:8001 --env-file .env --mount "type=bind,source=$((Get-Location).Path)/models,target=/app/models,readonly" steel-defect-api
```

Use an environment file with deployment-appropriate `ALLOWED_ORIGINS`. Preserve
container-relative model paths from `.env.example`; host absolute paths do not
exist inside the container. Mount only approved artifacts in a deployed environment,
rather than training datasets or old experiment outputs. The directory mount above is for
local verification. The non-root image user needs read permission on mounted files.

For optional cloud fallback, build with `--build-arg INSTALL_VERTEX=true`, then
explicitly configure `ENABLE_VERTEX_AI=true`, project, region, endpoint and runtime
credentials. Never copy credentials into the image. Local TFLite remains preferred.

Build the frontend separately after setting its public `VITE_API_BASE_URL`:

```powershell
npm --prefix frontend ci
npm --prefix frontend run build
```

Serve `frontend/dist/` with a static host configured to return `index.html` for SPA
routes. Vite's development server is not the production server. Browser variables
are public build inputs. The existing demo login does not provide API authorization.

Run one API worker initially because each worker keeps its own model instances.
Measure RAM under representative inference load before choosing a memory limit or
increasing workers. The API image still needs substantial PyTorch/TensorFlow disk
space; removing repository caches cannot eliminate runtime library requirements.

The container definition has not been built here because Docker is unavailable.
Lint, type, API fixture and browser checks validate the source reorganization;
container build, artifact permissions, real deployment smoke tests and the outstanding
correctness audit findings must be checked before production sign-off.
