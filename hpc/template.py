"""
Template: HPC Pipeline Script
=============================

This template lives in `hpc/`, paired with the CPU and GPU batch submit templates
(`hpc/batch_cpu/template`, `hpc/batch_gpu/template`). It provides the standard interface
between those batch scripts and PyAutoGalaxy modeling code: command-line argument parsing,
configuration setup, and dataset loading, so that the same script runs identically on a
local machine and on the HPC.

Copy this file into `scripts/` and rename it for your science case (e.g. `scripts/imaging.py`),
then fill in the `Model, Analysis & Search` section of `fit()` using scripts from
`autogalaxy_workspace/scripts/` as a reference. The batch templates run `scripts/$SCRIPT`, so
the copy belongs in `scripts/`. The HPC interface (`parse_fit_args`, `__main__`, `--use_cpu`,
`--number_of_cores`) must be preserved — the CPU and GPU batch templates depend on it, and
`scripts/AGENTS.md` documents it as the contract every pipeline in `scripts/` conforms to.

**What an array task is, here.** Galaxy structure work is usually *sample*-shaped: a few
hundred objects, each cheap on its own. So the unit of parallelism is one galaxy per SLURM
array task — not one stage of a pipeline per task. A sample of 200 galaxies is
`--array=0-199` over one dataset list, each task independent, each writing its own output
directory. There is no inter-task ordering to preserve and nothing to chain.

**Run times, to size the wall-clock request.** A single Sersic or a linear bulge-plus-disk
fit on a ~200x200 masked cutout is minutes on a GPU and tens of minutes on a few CPU cores.
A Multi-Gaussian Expansion costs little more in the non-linear search — its intensities are
solved by linear inversion rather than sampled, so the dimensionality barely moves — but each
likelihood evaluation is heavier. A pixelised reconstruction is the expensive case: hours, and
it is the one that wants the memory. Ask for what the *slowest* galaxy in the sample needs;
array tasks that finish early cost nothing.

This file is written in the project's generated-script style (title + `__Contents__`
header, with each section introduced by a triple-quoted `__Section__` docstring) — see the
project root `AGENTS.md` "Conventions" and `skills/_style.md` "Generated script style".
Keep that style when you adapt it.

__Contents__

- **Imports:** Import the required libraries.
- **Configuration:** Push the project `config/` and `output/` paths.
- **Dataset:** Load data, noise-map, PSF and metadata from `info.json`.
- **Settings:** Build `SettingsSearch` (output path prefix, unique tag).
- **Model, Analysis & Search:** Science-specific model-fit — fill this in.
- **HPC Interface:** `parse_fit_args()` and `__main__` — leave unchanged.

__HPC Interface (usage)__

GPU batch scripts call:

    python3 scripts/imaging.py --sample=<sample> --dataset=<dataset>

CPU batch scripts call:

    python3 scripts/imaging.py --sample=<sample> --dataset=<dataset> --use_cpu --number_of_cores=$THREADS

The `use_cpu` flag controls whether JAX is disabled for analysis objects
(`use_jax=not use_cpu`) and whether CPU-specific optimisations are applied. The
`number_of_cores` parameter controls Nautilus multicore parallelism on CPU runs; on GPU,
Nautilus uses a single core and JAX handles parallelism.
"""

"""
__Imports__

Standard library helpers plus the PyAuto* stack: `autofit` for the model and search,
`autogalaxy` for galaxies and light profiles, and `autonerves` for configuration.
"""
import json
import argparse
from pathlib import Path

import autofit as af
import autogalaxy as ag
from autonerves import conf


def fit(
    dataset_name: str,
    sample_name: str = None,
    iterations_per_quick_update: int = 5000,
    number_of_cores: int = 1,
    use_cpu: bool = False,
):
    """
    Fit a galaxy model to a single dataset.

    This function is called once per dataset, either from ``__main__`` (local)
    or from a SLURM array task (HPC). Add your science-specific model,
    analysis, and search code in the ``Model, Analysis & Search`` section below.

    Parameters
    ----------
    dataset_name
        Name of the dataset subdirectory inside ``dataset/<sample_name>/``.
    sample_name
        Name of the sample subdirectory inside ``dataset/``.
    iterations_per_quick_update
        Nautilus iterations between on-the-fly visualisation updates.
    number_of_cores
        Number of CPU cores for Nautilus (used on CPU runs only).
    use_cpu
        If True, disables JAX in analysis objects and enables CPU-specific
        optimisations. Set automatically by CPU batch scripts via ``--use_cpu``.
    """

    """
    __Configuration__

    Point PyAutoNerves at the project's `config/` YAML files and `output/` directory, so the
    same paths resolve identically on a local machine and on the HPC.
    """
    project_root = Path(__file__).parent.parent

    conf.instance.push(
        new_path=project_root / "config",
        output_path=project_root / "output",
    )

    """
    __Dataset__

    Load the imaging data, noise-map and PSF for this galaxy. All dataset-specific values
    (`pixel_scale`, `mask_radius`, `redshift`, ...) come from the dataset's `info.json` via
    `info.get(key, default)`, so nothing is hard-coded here and one script serves a whole
    sample. Loading and masking are handled by `ag.Imaging.from_fits` and `ag.Mask2D.circular`
    (`PyAutoArray:autoarray/dataset/imaging/dataset.py`, `PyAutoArray:autoarray/mask/mask_2d.py`).

    The mask radius is a science choice, not a default: a mask that truncates the outer
    isophotes biases the effective radius and Sersic index directly, so `mask_radius` belongs
    in each galaxy's `info.json` rather than being shared across the sample.

    For a multi-waveband dataset laid out as `dataset/<galaxy>/wavebands/<BAND>/` (the
    convention in `wiki/core/operations/dataset.md`), point the two arguments one level
    deeper — `--sample=<galaxy>/wavebands --dataset=F277W` — and each band becomes its own
    array task with its own `info.json`.
    """
    dataset_path = project_root / "dataset"

    if sample_name is not None:
        dataset_path = dataset_path / sample_name

    dataset_path = dataset_path / dataset_name

    info_path = dataset_path / "info.json"

    with open(info_path) as f:
        info = json.load(f)

    pixel_scale = info.get("pixel_scale", 0.06)
    mask_radius = info.get("mask_radius", 3.0)
    redshift = info.get("redshift", 0.5)

    dataset = ag.Imaging.from_fits(
        data_path=dataset_path / "data.fits",
        noise_map_path=dataset_path / "noise_map.fits",
        psf_path=dataset_path / "psf.fits",
        pixel_scales=pixel_scale,
    )

    mask = ag.Mask2D.circular(
        shape_native=dataset.shape_native,
        pixel_scales=dataset.pixel_scales,
        radius=mask_radius,
    )

    dataset = dataset.apply_mask(mask=mask)

    """
    __Settings__

    `SettingsSearch` controls the output path prefix (so each galaxy writes to its own
    subdirectory) and the unique tag that identifies this model-fit
    (`PyAutoFit:autofit/non_linear/settings.py`).

    The `unique_tag` matters more on a sample run than it does on a laptop: PyAutoFit's
    identifier is built from the model and the search settings, **not** from the data, so two
    array tasks fitting the same model to different galaxies would resume each other's output
    if the path prefix and tag did not separate them. The prefix below is per-galaxy for
    exactly that reason.
    """
    settings_search = af.SettingsSearch(
        path_prefix=(
            Path(sample_name) / dataset_name
            if sample_name is not None
            else Path(dataset_name)
        ),
        unique_tag="initial_galaxy_model",
        info=None,
        session=None,
    )

    """
    __Model, Analysis & Search__

    Fill in the science-specific model-fit here, using scripts from
    `autogalaxy_workspace/scripts/` as a reference (`imaging/start_here.py` for the canonical
    end-to-end run, `imaging/features/` for a basis, a pixelisation or a free sky). The four
    steps are:

    1. **Model** — define the galaxy's light with `af.Model` / `af.Collection`, e.g. a linear
       bulge and disk, or a Multi-Gaussian Expansion, on an `ag.Galaxy` at `redshift`.
    2. **Analysis** — create `ag.AnalysisImaging(dataset=dataset, use_jax=not use_cpu)`
       so JAX is enabled on GPU runs and disabled on CPU runs.
    3. **Search** — create `af.Nautilus`. On CPU runs, thread `number_of_cores` into the
       search via `{**settings_search.search_dict, "number_of_cores": number_of_cores}`;
       on GPU, `settings_search.search_dict` is sufficient.
    4. **Fit** — run `search.fit(model=model, analysis=analysis, **settings_search.fit_dict)`.

    Outputs land under `output/<path_prefix>/<name>/<unique_id>/`.
    """
    raise NotImplementedError(
        "Replace this with your science-specific model, analysis, and search steps. "
        "See autogalaxy_workspace/scripts/ for examples."
    )


"""
__HPC Interface__

`parse_fit_args()` reads the command-line arguments shared by every pipeline script and
`__main__` wires them into `fit()`. The CPU and GPU batch scripts depend on this interface —
leave it unchanged.
"""


def parse_fit_args():
    """
    Parse command-line arguments shared by all pipeline scripts.

    Returns
    -------
    tuple
        (sample_name, dataset_name, iterations_per_quick_update, number_of_cores, use_cpu)
    """
    parser = argparse.ArgumentParser(description="PyAutoGalaxy HPC Pipeline")

    parser.add_argument(
        "--sample",
        metavar="name",
        required=False,
        default=None,
        help="Sample subdirectory inside dataset/ containing the dataset.",
    )
    parser.add_argument(
        "--dataset",
        metavar="name",
        required=True,
        help="Name of the dataset subdirectory inside dataset/<sample>/.",
    )
    parser.add_argument(
        "--iterations_per_quick_update",
        metavar="int",
        required=False,
        default=5000,
        help="Number of sampler iterations between on-the-fly visualisation updates.",
    )
    parser.add_argument(
        "--number_of_cores",
        metavar="int",
        required=False,
        default=1,
        help="Number of CPU cores for non-JAX Nautilus searches.",
    )
    parser.add_argument(
        "--use_cpu",
        action="store_true",
        default=False,
        help="CPU mode: disables JAX and enables CPU-specific optimisations.",
    )

    args = parser.parse_args()

    return (
        args.sample,
        args.dataset,
        int(args.iterations_per_quick_update),
        int(args.number_of_cores),
        args.use_cpu,
    )


if __name__ == "__main__":
    sample_name, dataset_name, iterations_per_quick_update, number_of_cores, use_cpu = (
        parse_fit_args()
    )

    fit(
        dataset_name=dataset_name,
        sample_name=sample_name,
        iterations_per_quick_update=iterations_per_quick_update,
        number_of_cores=number_of_cores,
        use_cpu=use_cpu,
    )
