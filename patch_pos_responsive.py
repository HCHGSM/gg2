import re

with open('pos_erp/ui/views/pos_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Make POS card responsive instead of fixed
old_card_size = 'card.setFixedSize(240, 180)'
new_card_size = 'card.setMinimumSize(200, 160)\n            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)'

content = content.replace(old_card_size, new_card_size)

# Update the grid layout to reflow or at least stretch evenly
if "self.products_grid.setColumnStretch" not in content:
    # We will just rely on QSizePolicy.Expanding, QGridLayout handles this nicely if we allow it.
    pass

# Update POS view width so the sidebar doesn't squash the grid
content = content.replace("cart_frame.setFixedWidth(460)", "cart_frame.setMinimumWidth(350)\n        cart_frame.setMaximumWidth(450)\n        cart_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)")

with open('pos_erp/ui/views/pos_view.py', 'w', encoding='utf-8') as f:
    f.write(content)
