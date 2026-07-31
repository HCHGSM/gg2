import os

with open('pos_erp/ui/styles.py', 'w') as f:
    from fix_styles_tmp import STYLES_PY
    f.write(STYLES_PY)
