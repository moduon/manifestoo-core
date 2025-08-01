"""Information about core Odoo addons."""

import sys
from functools import lru_cache
from typing import Set

if sys.version_info >= (3, 9):
    from importlib.resources import files as package_files
else:
    from importlib_resources import files as package_files

from ..odoo_series import OdooEdition, OdooSeries

__all__ = [
    "get_core_addon_license",
    "get_core_addons",
    "is_core_addon",
    "is_core_ce_addon",
    "is_core_ee_addon",
]


@lru_cache()
def _get_core_addons(odoo_series: OdooSeries, odoo_edition: OdooEdition) -> Set[str]:
    with (
        package_files("manifestoo_core.core_addons")
        .joinpath(
            f"addons-{odoo_series.value}-{odoo_edition.value}.txt",
        )
        .open()
    ) as f:
        return {a.strip() for a in f if not a.startswith("#")}


@lru_cache()
def get_core_addons(odoo_series: OdooSeries) -> Set[str]:
    """Return the set of core Odoo addons for a given Odoo series."""
    return _get_core_addons(odoo_series, OdooEdition.CE) | _get_core_addons(
        odoo_series,
        OdooEdition.EE,
    )


def is_core_ce_addon(addon_name: str, odoo_series: OdooSeries) -> bool:
    """Test wether an addon is part of the Community Edition of a given Odoo series."""
    return addon_name in _get_core_addons(odoo_series, OdooEdition.CE)


def is_core_ee_addon(addon_name: str, odoo_series: OdooSeries) -> bool:
    """Test wether an addon is part of the Enterprise Edition of a given Odoo series."""
    return addon_name in _get_core_addons(odoo_series, OdooEdition.EE)


def is_core_addon(addon_name: str, odoo_series: OdooSeries) -> bool:
    """Test wether an addon is part of a given Odoo series."""
    return addon_name in get_core_addons(odoo_series)


def get_core_addon_license(addon_name: str, odoo_series: OdooSeries) -> str:
    """Get the license of a core Odoo addon.

    This function overrides any license set in the upstream addon
    manifest, as Odoo has a uniform license for each version and
    edition, and the manifests have been known to be unreliable in that
    respect.
    """
    if is_core_ce_addon(addon_name, odoo_series):
        if odoo_series == OdooSeries.v8_0:
            return "AGPL-3"
        return "LGPL-3"
    if is_core_ee_addon(addon_name, odoo_series):
        return "OEEL-1"
    msg = f"{addon_name} is not a core addon."  # pragma: no cover
    raise AssertionError(msg)  # pragma: no cover
