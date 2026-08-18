def install_performance_patch():
    """
    Install the corrected ranking calculator into the frozen compatibility core.
    The legacy file itself is not edited; dashboard routes resolve this global
    function at request time, so the patch is isolated and reversible.
    """
    import legacy_core
    from .service import corrected_am_business_month_rankings
    legacy_core.am_business_month_rankings=corrected_am_business_month_rankings
