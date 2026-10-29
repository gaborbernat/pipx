Where pipx copies launchers instead of linking them, as on Windows without symlink rights, ``pipx reinstall`` no longer
warns ``Overwriting file`` for the package's own launchers. Windows ``.exe`` launchers embed their build time, so a
rebuilt one never matched its old copy byte for byte and every reinstall warned. pipx now recognises its own copy by the
interpreter it names and replaces it quietly; a file from another venv or the user still gets the warning.
