# backend/app/core/settings.py
# LifeLink AI — Settings Re-export
# Architecture Reference: ARCHITECTURE.md Section 16 (Backend Architecture)
#
# This file re-exports the settings object from app.config for convenience.
# Some modules may prefer: from app.core.settings import settings
# Both import paths work identically.
#
# The canonical source of truth is app/config.py (Settings class).

from app.config import Settings, get_settings, settings

__all__ = ["Settings", "get_settings", "settings"]
